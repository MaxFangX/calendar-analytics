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
        filterData.end.toISOString() + " " +
        filterData.calendarIds.join(' ');


      $rootScope.$broadcast('calendarFilter:updated');
    }
  };
}]);

analyticsApp.service("TagService", ['$http', '$q', function($http, $q) {

  var _this = this;

  this.tags = {};

  this.getTags = function(filterKey, start, end, calendarIds) {

    if (!filterKey) {
      throw "filterKey must always be supplied";
    }

    if (start || end) {
      // If the start and end time match the given filterKey
      var keyFromParameters = start.toISOString() + " " + end.toISOString() +
        " " + calendarIds.join(' ');
      if (filterKey !== keyFromParameters) {
        throw "filterKey doesn't match given start and end times";
      }
    }
    // Attempt to return cached tags
    if (_this.tags[filterKey]) {
      return $q.when(_this.tags[filterKey]);
    }

    // Request the tags and return a promise
    return $http({
      method: 'GET',
      url: '/v1/tags.json',
      cache: true,
      params: {
        start: (start)? start.toISOString() : null,
        end: (end)? end.toISOString() : null,
        calendar_ids: JSON.stringify(calendarIds),
        timezone: moment.tz.guess()
      }
    }).then(function successCallback(response) {
      _this.tags[filterKey] = [];
      for (var i = 0; i < response.data.results.length; i++) {
        var tag = response.data.results[i];
        _this.tags[filterKey].push({
          id: tag.id,
          label: tag.label,
          keywords: tag.keywords,
          hours: tag.hours
        });
      }
      return _this.tags[filterKey];
    }, function errorCallback(response) {
      /* jshint unused:vars */
      console.log("Failed to get tags:");
      console.log(response);
    });
  };

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
    if (!filterKey) {
      throw "filterKey must always be supplied";
    }

    if (start || end) {
      // If the start and end time match the given filterKey
      var keyFromParameters = start.toISOString() + " " + end.toISOString() +
        " " + calendarIds.join(' ');
      if (filterKey !== keyFromParameters) {
        throw "filterKey doesn't match given start, end, and calendarIds";
      }
    }

    // Attempt to return cached categories
    if (_this.categories[filterKey]) {
      return $q.when(_this.categories[filterKey]);
    }

    // Request the categories and return a promise
    return $http({
      method: 'GET',
      url: '/v1/categories.json',
      cache: true,
      params: {
        start: (start)? start.toISOString() : null,
        end: (end)? end.toISOString() : null,
        calendar_ids: JSON.stringify(calendarIds),
        timezone: moment.tz.guess()
      }
    }).then(function successCallback(response) {
      _this.categories[filterKey] = [];
      for (var i = 0; i < response.data.results.length; i++) {
        var category = response.data.results[i];
        _this.categories[filterKey].push({
          id: category.id,
          label: category.label,
          hours: category.hours,
          include: true,
          color: category.category_color,
        });
      }
      return _this.categories[filterKey];
    }, function errorCallback(response) {
      /* jshint unused:vars */
      console.log("Failed to get categories");
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

analyticsApp.service('QueryService', ['$http', '$q', function($http, $q) {

  var _this = this;

  this.details = {};

  this.populateData = function(filterKey, type, id, timeStep, data) {
    // Attempt to return cached categories
    if (_this.details[filterKey]) {
      return _this.details[filterKey];
    }

    var dailyData = data.lineGraph[0].values
    var ctrlDetails = [];

    // Type line
    var timeStepData = [];
    // Gets hours of first datapoint
    var start = new Date(dailyData[0].x)
    var offset = 0;

    if (timeStep == "week") {
      // Find closest Monday
      start.setDate(start.getDate() - start.getDay() + (start.getDay() == 0 ? -6:1));
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
        endOfTimeStep = (i + offset) % 7 == 0;
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
            first_event = 0
          } else {
            first_event = timeStepData[data_point - period].y;
          }
          moving_average = moving_average - first_event + timeStepHours;
          movingAverageList.push({
            x: new Date(start),
            y: moving_average / period
          })
        }
        data_point += 1

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
      endOfTimeStep = (i + offset) % 7 != 0;
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
        })
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
  }

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
      var data = response.data
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
}]);

analyticsApp.service('CalendarSelect', ['$http', '$q', function($http, $q) {
  this.calendars = {};
  var _this = this;

  this.initialize = function(response) {
    // Initialize cached calendars
    for (var i = 0; i < response.data.results.length; i++) {
      var gcal = response.data.results[i];
      if (_this.calendars[gcal.calendar_id] === undefined) {
        _this.calendars[gcal.calendar_id] = gcal;
        _this.calendars[gcal.calendar_id].enabled = gcal.enabled_by_default;
      }
    }
  }

  // Converts the dict of calendarIds to an array of ids of enabled calendars
  this.getEnabledCalendarIds = function() {
    var calendarIds = Object.values(_this.calendars)
      .filter(function(cal) {
        return cal.enabled ? true : false;
      })
      .map(function(cal) {
        return cal.calendar_id;
      })
      .sort();
    return calendarIds;
  };
}]);
