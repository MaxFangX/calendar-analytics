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
      return $q.when(
        QueryService.getDataForCalendarId("tags", start, end, calId, _this.tags, cacheKey));
    });

    var accumulatedTags = {};
    var tags = [];

    return $q.all(calendarData).then(function successCallback(response) {
      // Add up duplicate tags across calendars.
      response.forEach(function(data) {
        for (var tagId in data) {
          if (accumulatedTags.hasOwnProperty(tagId.toString())) {
            accumulatedTags[tagId].hours += data[tagId].hours;
          } else {
            accumulatedTags[tagId] = data[tagId];
          }
        }
      });
      // Construct the data for tag details.
      for (var tag in accumulatedTags) {
        tags.push({
          id: tag,
          label: accumulatedTags[tag].label,
          keywords: accumulatedTags[tag].keywords,
          hours: accumulatedTags[tag].hours
        });
      }
      return tags;
    }, function errorCallback(response) {
      console.log("Failed to get tags");
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

analyticsApp.service('CategoryService', ['$http', '$q', 'QueryService', function($http, $q, QueryService) {

  var _this = this;

  this.categories = {};

  this.getCategories = function(filterKey, start, end, calendarIds) {

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

    var calendarData = calendarIds.map(function(calId) {
      var cacheKey = calId + " " + filterKey;
      return $q.when(
        QueryService.getDataForCalendarId("categories", start, end, calId, _this.categories, cacheKey));
    });

    var accumulatedCategories = {};
    var categories = [];

    return $q.all(calendarData).then(function successCallback(response) {
      // Add up duplicate categories across calendars.
      response.forEach(function(data) {
        for (var categoryId in data) {
          if (accumulatedCategories.hasOwnProperty(categoryId.toString())) {
            accumulatedCategories[categoryId].hours += data[categoryId].hours;
          } else {
            accumulatedCategories[categoryId] = data[categoryId];
          }
        }
      });
      // Construct the data for category details.
      for (var category in accumulatedCategories) {
        categories.push({
          id: category,
          label: accumulatedCategories[category].label,
          color: accumulatedCategories[category].color,
          hours: accumulatedCategories[category].hours
        });
      }
      return categories;
    }, function errorCallback(response) {
      console.log("Failed to get categories");
    });
  }.bind(this);

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

analyticsApp.service('QueryService', ['$http', '$q', function($http, $q) {

  var _this = this;

  this.details = {};

  this.populateData = function(filterKey, type, id, timeStep, data) {
    // Attempt to return cached categories
    if (_this.details[filterKey]) {
      return _this.details[filterKey];
    }

    var dailyData = data.lineGraph[0].values;
    var ctrlDetails = [];

    // Type line
    var timeStepData = [];
    // Gets hours of first datapoint
    var start = new Date(dailyData[0].x);
    var offset = 0;

    if (timeStep == "week") {
      // Find closest Monday
      start.setDate(start.getDate() - start.getDay() + (start.getDay() === 0 ? -6:1));
      offset = start.getDay();
    }
    if (timeStep == "month") {
      offset = start.getDate();
      start.setDate(1);
    }

    var timeStepHours = 0;
    var maxYValue = 0;

    // Trendline
    var xLabels = [];
    var yLabels = [];

    // Moving average
    var movingAverageList = [];
    var data_point = 0;
    var moving_average = 0;
    var period = 7;
    var endOfTimeStep = true;

    for (var i = 0; i < dailyData.length; i++) {
      timeStepHours += dailyData[i].y;

      if (timeStep == "week") {
        endOfTimeStep = (i + offset) % 7 === 0;
      }
      if (timeStep == "month") {
        endOfTimeStep = offset == new Date(start.getYear(), start.getMonth() + 1, 0).getDate();
        offset += 1;
      }

      if (endOfTimeStep) {
        xLabels.push(new Date(start));
        yLabels.push(timeStepHours);

        timeStepData.push({
          x: new Date(start),
          y: timeStepHours
        });

        // Max Y Value logic
        if (timeStepHours > maxYValue) {
          maxYValue = timeStepHours;
        }

        // Moving average logic.
        if (data_point < period - 1) {
          moving_average += timeStepHours;
        } else {
          if (data_point - period == -1) {
            first_event = 0;
          } else {
            first_event = timeStepData[data_point - period].y;
          }
          moving_average = moving_average - first_event + timeStepHours;
          movingAverageList.push({
            x: new Date(start),
            y: moving_average / period
          });
        }
        data_point += 1;

        timeStepHours = 0;
        if (timeStep == "week") {
          start.setDate(start.getDate() + 7);
        }
        if (timeStep == "month") {
          offset = 1;
          start.setMonth(start.getMonth() + 1);
        }
      }
    }

    if (timeStep == "week") {
      endOfTimeStep = (i + offset) % 7 !== 0;
    }
    if (timeStep == "month") {
      endOfTimeStep = offset != new Date(start.getYear(), start.getMonth() + 1, 0).getDate();
    }
    // Take care of this week/month
    if (endOfTimeStep) {
      xLabels.push(new Date(start));
      yLabels.push(timeStepHours);
      timeStepData.push({
        x: new Date(start),
        y: timeStepHours
      });

      if (data_point > period - 1) {
        // Moving average for this week/month
        first_event = timeStepData[data_point - period].y;
        moving_average = moving_average - first_event + timeStepHours;
        movingAverageList.push({
          x: new Date(start),
          y: moving_average / period
        });
      }
    }

    var trendData = trendLine(xLabels, yLabels);

    ctrlDetails.push({
      values: timeStepData,
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

    ctrlDetails.push({
      values: movingAverageList,
      key: '7D Moving Average Line',
      color: '#003057',
      strokeWidth: 3,
    });

    _this.details[filterKey] = {lineGraph: ctrlDetails, maxYValue: maxYValue + 10};
    return _this.details[filterKey];
  };

  this.populateDay = function(filterKey, type, id, calendarIds) {
    if (!filterKey) {
      throw "filterKey must always be supplied";
    }

    // Attempt to return cached categories
    if (_this.details[filterKey]) {
      return $q.when(_this.details[filterKey]);
    }

    var timeseriesUrl = "";
    if (type == "Category") {
      timeseriesUrl = '/v1/categories/' + id + '/timeseries/day';
    } else {
      timeseriesUrl = '/v1/tags/' + id + '/timeseries/day';
    }
    return $http({
      method: 'GET',
      url: timeseriesUrl + '.json',
      params: {
        timezone: moment.tz.guess(),
        calendar_ids: JSON.stringify(calendarIds)
      }
    }).then(function successCallback(response) {
      var data = response.data;
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

      var trendData = trendLine(xLabels, yLabels);

      // This line should always be pushed on first
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
      _this.details[filterKey] = {lineGraph: ctrlDetails, maxYValue: maxYValue};
      return _this.details[filterKey];
    });
  };


  function trendLine(xLabels, yLabels) {
    var xSeries = d3.range(1, xLabels.length + 1);
    var leastSquaresCoeff = leastSquares(xSeries, yLabels);

    // apply the results of the least squares regression
    var x1 = xLabels[0];
    var y1 = leastSquaresCoeff[0] + leastSquaresCoeff[1];
    var x2 = xLabels[xLabels.length - 1];
    var y2 = leastSquaresCoeff[0] * xSeries.length + leastSquaresCoeff[1];
    return [{x:x1,y:y1},{x:x2,y:y2}];

  }

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

  this.getDataForCalendarId = function(type, start, end, calendarId, cache, cacheKey) {
 //    As an example, tags are saved like this:
 //    [
 //     cacheKey1:
 //       {
 //         tagId1: {hours: 5, label: "school", keywords: "UC Berkeley"},
 //         tagId2: {hours: 5, label: "music", keywords: "The All-American Rejects"}
 //       },
 //     cacheKey2:
 //       {
 //         tagId1: {hours: 5, label: "school", keywords: “UC Berkeley”},
 // 	      tagId2: {hours: 5, label: "music", keywords: “The All-American Rejects”}
 // 	    }
 //     ]
    var calendarData = {};
    if (cache[cacheKey]) {
      calendarData = angular.copy(cache[cacheKey]);
      return calendarData;
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
        modelData.forEach(function(model) {
          if (calendarData.hasOwnProperty(model.id.toString())) {
            calendarData[model.id].hours += model.hours;
          } else {
            if (type === 'tags') {
              calendarData[model.id] = {
                hours: model.hours, label: model.label, keywords: model.keywords
              };
            }
            if (type === 'categories') {
              calendarData[model.id] = {
                hours: model.hours, label: model.label, color: model.category_color
              };
            }
          }
        });
        // Save the data in the cache.
        cache[cacheKey] = angular.copy(calendarData);
        return calendarData;
      });
    }
  };
}]);
