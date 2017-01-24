/*jslint devel: true, browser: true, jquery: true */
/*global d3, getCookie, moment */

var analyticsApp = window.angular.module('analyticsApp.services', []);

analyticsApp.factory('CalendarFilterService', ['$rootScope', function CalendarFilterService($rootScope) {
  var filterData =  {
    start: undefined, // Moment object
    end: undefined, // Moment object
    calendarIds: undefined, // array of ids of enabled calendars
    filterKey: undefined,
  };

  return {
    getFilter: function() {
      return filterData;
    },
    setFilter: function(start, end, calendarIds) {
      if (start !== null && start !== undefined) {
        filterData.start = start;
      }
      if (end !== null && end !== undefined) {
        filterData.end = end;
      }
      if (calendarIds !== null && calendarIds !== undefined) {
        filterData.calendarIds = calendarIds;
      }

      // Key must be unique per selection of start/end/calendarIds
      filterData.filterKey = filterData.start.toISOString() + " " +
        filterData.end.toISOString();


      $rootScope.$broadcast('calendarFilter:updated');
    }
  };
}]);

analyticsApp.service("TagService", ['$http', '$q', 'QueryService', function($http, $q, QueryService) {

  var _this = this;

  this.tags = {};

  this.getTags = function(filterKey, start, end, calendarIds) {

    if (!filterKey) {
      throw "filterKey must always be supplied";
    }

    if (start || end) {
      // If the start and end time match the given filterKey
      var keyFromParameters = start.toISOString() + " " + end.toISOString();
      if (filterKey !== keyFromParameters) {
        throw "filterKey doesn't match given start and end times";
      }
    }

    var calendarData = calendarIds.map(function(calId) {
      var cacheKey = calId + " " + filterKey;
      _this.tags[cacheKey] = $q.when(QueryService.getDataForCalendarIds("tags", start, end, calId, _this.tags, cacheKey));
      return $q.when(_this.tags[cacheKey]);
    });

    var accumulatedTags = {};
    var tags = [];

    return $q.all(calendarData).then(function(response) {
      response.forEach(function(data) {
        for (var tagId in data) {
          if (accumulatedTags.hasOwnProperty(tagId)) {
            accumulatedTags[tagId].hours = accumulatedTags[tagId].hours + data[tagId].hours;
          } else {
            accumulatedTags[tagId] = data[tagId];
          }
        }
      });
      for (var tag in accumulatedTags) {
        tags.push({
          id: tag,
          label: accumulatedTags[tag].label,
          keywords: accumulatedTags[tag].keywords,
          hours: accumulatedTags[tag].hours
        });
      }
      return tags;
    });

  }.bind(this);

  this.createTag = function(label, keywords, isCumulative, filterData) {
    return $http({
      method: 'POST',
      url: '/v1/tags.json',
      data: $.param({
        label: label,
        keywords: keywords,
        csrfmiddlewaretoken: getCookie('csrftoken')
      }),
      params: {
        start: isCumulative ? null : filterData.start.toISOString(),
        end: isCumulative ? null : filterData.end.toISOString(),
        calendar_ids: JSON.stringify(filterData.calendarIds),
        timezone: moment.tz.guess()
      },
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
  };

  this.editTag = function(tagId, newLabel, newKeywords, isCumulative, filterData) {
    return $http({
      method: 'POST',
      url: '/v1/tags/' + tagId,
      data: $.param({
        label: newLabel,
        keywords: newKeywords,
        csrfmiddlewaretoken: getCookie('csrftoken'),
        _method: 'PATCH'
      }),
      params: {
        start: isCumulative ? null : filterData.start.toISOString(),
        end: isCumulative ? null : filterData.end.toISOString(),
        calendar_ids: JSON.stringify(filterData.calendarIds),
        timezone: moment.tz.guess()
      },
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    }).then(function successCallback(response) {
      var filterKey = isCumulative ? 'cumulative ' + filterData.filterKey : filterData.filterKey;
      _this.tags[filterKey] = null;
      return response.data;
    }, function errorCallback() {
      console.log("Failed to edit tag with id " + tagId);
      return null;
    });
  };

  this.deleteTag = function(tagId) {
    return $http({
      method: 'POST',
      url: '/v1/tags/' + tagId,
      data: $.param({
        csrfmiddlewaretoken: getCookie('csrftoken'),
        _method: 'DELETE'
      }),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
  };

}]);

analyticsApp.service('CategoryService', ['$http', '$q', function($http, $q) {

  var _this = this;

  this.categories = {};

  this.getCategories = function(filterKey, start, end, calendarIds) {
    var calendarCategories = {}; // {calendarId : list of categories}
    var accumulatedCategories = {};
    var requests = [];
    var calendarRequestsMap = {}; // {request index : calendarId}
    var categories = [];

    if (!filterKey) {
      throw "filterKey must always be supplied";
    }

    if (start || end) {
      // If the start and end time match the given filterKey
      var keyFromParameters = start.toISOString() + " " + end.toISOString();
      if (filterKey !== keyFromParameters) {
        throw "filterKey doesn't match given start, end, and calendarIds";
      }
    }

    for (var i = 0; i < calendarIds.length; i++) {
      var cacheKey = calendarIds[i] + " " + filterKey;
      if (this.categories[cacheKey]) {
        calendarCategories[calendarIds[i]] = this.categories[cacheKey];
      } else {
        requests.push($http({
          method: 'GET',
          url: '/v1/categories.json',
          cache: true,
          params: {
            start: (start)? start.toISOString() : null,
            end: (end)? end.toISOString() : null,
            calendar_ids: JSON.stringify([calendarIds[i]]),
            timezone: moment.tz.guess()
          }
        }));
        calendarRequestsMap[i] = calendarIds[i];
      }
    }

    return $q.all(requests).then(function(responses) {
      for (var j = 0; j < responses.length; j++) {
        var data = responses[j].data.results;
        var calId = calendarRequestsMap[j];
        var cacheKey = calId + " " + filterKey;
        calendarCategories[calId] = data;
        _this.categories[cacheKey] = data;
      }

      for (var calendar in calendarCategories) {
        for (var n = 0; n < calendarCategories[calendar].length; n++) {
          var category = calendarCategories[calendar][n];
          if (accumulatedCategories.hasOwnProperty(category.id)) {
            var categoryInfo = accumulatedCategories[category.id];
            categoryInfo[2] += category.hours;
            accumulatedCategories[category.id] = categoryInfo;
          } else {
            accumulatedCategories[category.id] =
              [category.label, category.category_color, category.hours];
          }
        }
      }

      for (var categoryId in accumulatedCategories) {
        if (accumulatedCategories.hasOwnProperty(categoryId)) {
          categories.push({
            label: accumulatedCategories[categoryId][0],
            id: categoryId,
            include: true,
            color: accumulatedCategories[categoryId][1],
            hours: accumulatedCategories[categoryId][2]
          });
        }
      }
      return categories;
    }, function errorCallback(response) {
      console.log("Failed to get categories:");
      console.log(response);
    });
  };

  this.editCategory = function(categoryId, newLabel) {
    return $http({
      method: 'POST',
      url: '/v1/categories/' + categoryId,
      data: $.param({
        label: newLabel,
        csrfmiddlewaretoken: getCookie('csrftoken'),
        _method: 'PATCH'
      }),
      params: {
        timezone: moment.tz.guess()
      },
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    }).then(function successCallback(response) {
      return response.data;
    }, function errorCallback() {
      console.log("Failed to edit category with id " + categoryId);
      return null;
    });
  };

  this.deleteCategory = function(categoryId) {
    return $http({
      method: 'POST',
      url: '/v1/categories/' + categoryId,
      data: $.param({
        csrfmiddlewaretoken: getCookie('csrftoken'),
        _method: 'DELETE'
      }),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
  };

}]);

analyticsApp.service('QueryService', ['$http', function($http) {
  this.populateData = function(data, type) {
    var ctrlDetails = [];
    var maxYValue = 0;
    var events = [];
    var movingAverage = [];
    var xLabels = [];
    var yLabels = [];
    for (var i = 0; i < data[0].length; i++) {
      var event = data[0][i];
      var date = new Date(event[0]);
      var hours = event[1];
      if (hours > maxYValue) {
        maxYValue = hours;
      }
      xLabels.push(date);
      yLabels.push(hours);
      events.push({
        x: date,
        y: hours
      });

      if (i < data[1].length) {
        // MA = Moving Average
        var MAEvent = data[1][i];
        var MADate = new Date(MAEvent[0]);
        var MAHours = MAEvent[1];
        movingAverage.push({
          x: MADate,
          y: MAHours
        });
      }
    }
    var xSeries = d3.range(1, xLabels.length + 1);
    var leastSquaresCoeff = leastSquares(xSeries, yLabels);

    // apply the results of the least squares regression
    var x1 = xLabels[0];
    var y1 = leastSquaresCoeff[0] + leastSquaresCoeff[1];
    var x2 = xLabels[xLabels.length - 1];
    var y2 = leastSquaresCoeff[0] * xSeries.length + leastSquaresCoeff[1];
    var trendData = [{x:x1,y:y1},{x:x2,y:y2}];

    ctrlDetails.push({
      values: events,
      key: type + ' Line',
      color: '#DDD5C7',
      strokeWidth: 2,
    });

    ctrlDetails.push({
      values: trendData,
      key: 'Trend Line',
      color: '#FDB515',
      strokeWidth: 3,
    });

    if (movingAverage.length != 1) {
      ctrlDetails.push({
        values: movingAverage,
        key: '7D Moving Average Line',
        color: '#003057',
        strokeWidth: 3,
      });
    }

    return [ctrlDetails, maxYValue];
  };

  // returns slope, intercept and r-square of the line
  function leastSquares(xSeries, ySeries) {
    var reduceSumFunc = function(prev, cur) { return prev + cur; };

    var xBar = xSeries.reduce(reduceSumFunc) * 1.0 / xSeries.length;
    var yBar = ySeries.reduce(reduceSumFunc) * 1.0 / ySeries.length;

    var ssXX = xSeries.map(function(d) { return Math.pow(d - xBar, 2); })
    .reduce(reduceSumFunc);

    var ssYY = ySeries.map(function(d) { return Math.pow(d - yBar, 2); })
    .reduce(reduceSumFunc);

    var ssXY = xSeries.map(function(d, i) { return (d - xBar) * (ySeries[i] - yBar); })
    .reduce(reduceSumFunc);

    var slope = ssXY / ssXX;
    var intercept = yBar - (xBar * slope);
    var rSquare = Math.pow(ssXY, 2) / (ssXX * ssYY);

    return [slope, intercept, rSquare];
  }

  this.getDataForCalendarIds = function(type, start, end, calendarId, cache, cacheKey) {
 //    As an example, tags are saved like this:
 //    [
 //     cacheKey1:
 //       {
 //         tagId1: {totalHours: 5, label: school, keywords: “UC Berkeley”},
 //         tagId2: {totalHours: 5, label: exercise, tag.keywords: “Gym”}
 //       },
 //     cacheKey2:
 //       {
 //         tagId1: {totalHours: 5, label: school, keywords: “UC Berkeley”},
 // 	      tagId2: {totalHours: 5, label: exercise, keywords: “Gym”}
 // 	    }
 //     ]

    if (cache[cacheKey]) {
      return cache[cacheKey];
    } else {
      return $http({
        method: 'GET',
        url: '/v1/' + type + '.json',
        cache: true,
        params: {
          start: (start)? start.toISOString() : null,
          end: (end)? end.toISOString() : null,
          calendar_ids: JSON.stringify([calendarId]),
          timezone: moment.tz.guess()
        }
      }).then(function successCallback(response) {
        var modelData = response.data.results;
        cache[cacheKey] = {};
        for (var i = 0; i < modelData.length; i++) {
          var model = modelData[i];
          if (cache[cacheKey].hasOwnProperty(model.id)) {
            var newHours = cache[cacheKey][model.id][hours] + model.hours;
            cache[cacheKey][model.id][hours] = newHours;
          } else {
            if (type === 'tags') {
              cache[cacheKey][model.id] = {
                hours: model.hours, label: model.label, keywords: model.keywords
              };
            }
            if (type === 'categories') {
              cache[cacheKey][model.id] = {
                hours: model.hours, label: model.label, color: model.category_color
              };
            }
          }
        }
        return cache[cacheKey];
      });
    }
  };
}]);
