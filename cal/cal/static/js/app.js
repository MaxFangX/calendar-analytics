var analyticsApp = angular.module('analyticsApp', ['nvd3', 'ui.calendar']);

analyticsApp.controller('LoggedInCtrl', function LoggedInController($scope) {
});

analyticsApp.factory('CalendarRangeService', ['$rootScope', function CalendarRangeService($rootScope) {
  var rangeData =  {
    start: undefined, // ISO String
    end: undefined, // ISO String
    timeRange: undefined,
    type: undefined,
  }

  return {
    getRange: function() {
      return rangeData;
    },
    setRange: function(start, end, type) {
      rangeData.start = start;
      rangeData.end = end;
      rangeData.type = type;
      rangeData.timeRange = rangeData.start.toISOString() + " " + rangeData.end.toISOString();
      $rootScope.$broadcast('calendarRange:updated');
    }
  }
}]);

function TagListCtrl($scope, $http, CalendarRangeService) {

  var _this = this;
  var tagUrl = '/v1/tags';

  this.tags = {};

  $scope.$on('calendarRange:updated', function(event, data) {
    var rangeData = CalendarRangeService.getRange();
    var timeRange;
    if (_this.isCumulative) {
      _this.updateTags('cumulative', null, null);
    } else {
      _this.updateTags(rangeData.timeRange, rangeData.start, rangeData.end)
    }
  });

  this.updateTags = function updateTags(timeRange, start, end) {
    _this.timeRange = timeRange;
    $http({
      method: 'GET',
      url: tagUrl + '.json',
      cache: true,
      params: {
        start: (start)? start.toISOString() : null,
        end: (end)? end.toISOString() : null,
      }
    })
      .success(function successCallback(data) {
        _this.tags[timeRange] = [];
        for (var i = 0; i < data.results.length; i++) {
          var tag = data.results[i];
          _this.tags[timeRange].push({
            id: tag.id,
            label: tag.label,
            keywords: tag.keywords,
            hours: tag.hours
          });
        }
      });
  }
  if (this.isCumulative) {
    this.updateTags('cumulative', null, null);
  } else {
    var initialTimeRange = CalendarRangeService.getRange()
    this.updateTags(initialTimeRange.timeRange, initialTimeRange.start, initialTimeRange.end);
  }

  this.hideZeroHoursFilter = function (value, index, array) {
    if (this.hideZeroHours && value.hours === 0) {
      return false;
    } else {
      return true;
    }
  }.bind(this);

  this.create = function(tag) {
    $http({
      method: 'POST',
      url: tagUrl + '.json',
      data: $.param({
        label: tag.label,
        keywords: tag.keywords,
        csrfmiddlewaretoken: getCookie('csrftoken')
      }),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    }).
    success(function addToList(data) {
      this.tags[this.timeRange].push({
        id: data.id,
        label: data.label,
        keywords: data.keywords,
        hours: data.hours,
        editing: false
      });
    });
  }.bind(this);

  this.startEdit = function(tagId) {
    var tag = this.tags[this.timeRange].find(function(tag, index, array) { return tag.id == tagId; });
    tag.newLabel = tag.label;
    tag.newKeywords = tag.keywords;
    tag.editing = true;
  };

  this.submit = function(tagId) {
    var tag = this.tags[this.timeRange].find(function(tag, index, array) { return tag.id == tagId; });
    tag.editing = false;

    var addToList = function addToList(data) {
      tag.label = data.label;
      tag.keywords = data.keywords;
      tag.hours = data.hours;
    }.bind(this);

    $http({
      method: 'POST',
      url: tagUrl + '/' + tagId,
      data: $.param({
        label: tag.newLabel,
        keywords: tag.newKeywords,
        csrfmiddlewaretoken: getCookie('csrftoken'),
        _method: 'PATCH'
      }),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    }).success(addToList);
  }.bind(this);

  this.cancelEdit = function(tagId) {
    var tag = this.tags[this.timeRange].find(function(tag, index, array) { return tag.id == tagId; });
    tag.editing = false;
  }.bind(this);

  this.delete = function(tagId) {
    $http({
      method: 'POST',
      url: tagUrl + '/' + tagId,
      data: $.param({
        csrfmiddlewaretoken: getCookie('csrftoken'),
        _method: 'DELETE'
      }),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    }).success(function removeFromList(data) {
      this.tags[this.timeRange] = this.tags[this.timeRange].filter(function(tag) {
        return tag.id !== tagId;
      });
    });
  }.bind(this);
};

analyticsApp.component('tagList', {
  templateUrl: '/static/templates/tag-list.html',
  controller: ['$scope', '$http', 'CalendarRangeService', TagListCtrl],
  controllerAs: '$ctrl',
  bindings: {
    isCumulative: '<?',
    displayName: '@',
    hideZeroHours: '<?'
  }
});

analyticsApp.controller('CategoriesCtrl', function($scope, $http){
  var categoryUrl = '/v1/colorcategories';
  $scope.categories = [];

  // populate the categories pie chart
  $http({ method: 'GET', url: categoryUrl + '.json' }).
    success(function successCallback(data) {
      for (var i = 0; i < data.results.length; i++) {
        var category = data.results[i];
        $scope.categories.push({
          id: category.id,
          label: category.label,
          hours: category.hours,
          include: true
        });
      }
    });

  this.startEdit = function(categoryId) {
    var category = $scope.categories.find(function(category, index, array) {
      return category.id == categoryId;
    });
    category.newLabel = category.label;
    category.editing = true;
  };

  this.submit = function(categoryId) {
    var category = $scope.categories.find(function(category, index, array) {
      return category.id == categoryId;
    });
    category.editing = false;

    $http({
      method: 'POST',
      url: categoryUrl + '/' + categoryId,
      data: $.param({
        label: category.newLabel,
        csrfmiddlewaretoken: getCookie('csrftoken'),
        _method: 'PATCH'
      }),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    }).
      success(function addToList(data) {
        category.label = data.label;
        category.hours = data.hours;
      });
  };


  this.cancelEdit = function(categoryId) {
    var category = $scope.categories.find(function(category, index, array) {
      return category.id == categoryId;
    });
    category.editing = false;
  };

  this.remove = function(categoryId) {
    $http({
      method: 'POST',
      url: categoryUrl + '/' + categoryId,
      data: $.param({
        csrfmiddlewaretoken: getCookie('csrftoken'),
        _method: 'DELETE'
      }),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    }).
      success(function removeFromList(data) {
        $scope.categories = $scope.categories.filter(function(category) {
          return category.id !== categoryId;
        });
      });
  };

  // categories pie chart
  $scope.options = {
    chart: {
      type: 'pieChart',
      height: 400,
      x: function(d){return d.label;},
      y: function(d){return d.hours;},
      showLabels: false,
      growOnHover: true,
      duration: 500,
      labelThreshold: 0.01,
      labelSunbeamLayout: true,
      legend: {
        margin: {
          top: 5,
          right: 0,
          bottom: 0,
          left: 0
        }
      },
    },
  };

});

analyticsApp.controller('CalendarCtrl', function CalendarCtrl($scope, $http, $q, uiCalendarConfig, CalendarRangeService) {

  $scope.calendars = {};

  this.events = function(start, end, timezone, callback) {
    var query_timezone = '';
    if (!timezone) {
      query_timezone = 'UTC';
    } else if (timezone === 'local') {
      query_timezone = moment.tz.guess();
    } else {
      query_timezone = timezone;
    }
    allEvents = [];

    $http({
      method: 'GET',
      url: "/v1/gcalendars.json",
      cache: true,
    }).then(function gcalSuccess(response) {

      var collectedEvents = [];
      var eventPromises = response.data.results.map(function(gcal) {

        // Initialize cached calendars
        if ($scope.calendars[gcal.calendar_id] === undefined) {
          $scope.calendars[gcal.calendar_id] = gcal;
          $scope.calendars[gcal.calendar_id].enabled = gcal.enabled_by_default;
        }

        return $http({
          method: 'GET',
          url: "/v1/gevents.json",
          cache: true,
          params: {
            calendarId: gcal.calendar_id,
            start: start.toISOString(),
            end: end.toISOString(),
            timezone: query_timezone,
            edge: 'truncated'
          },
        }).then(function eventSuccess(response) {
          var events = [];
          $.each(response.data.results, function(index, gevent) {
            events.push({
              title: gevent.name,
              start: gevent.start,
              end: gevent.end,
              allDay: gevent.all_day_event,
              backgroundColor: gevent.color.background,
              textColor: gevent.color.foreground,
              borderColor: gevent.color.foreground,
              description: gevent.description,
              location: gevent.location,
            });
          });

          if ($scope.calendars[gcal.calendar_id].enabled) {
            collectedEvents = collectedEvents.concat(events);
          }
        }, function eventError(response) {
          console.log("Ajax call to gevents failed: " + response);
        });
      });

      $q.all(eventPromises).then(function() {
        callback(collectedEvents);
      });

    }, function gcalError(response) {
      console.log("Ajax call to gcalendars failed: " + response);
    });

  };
  $scope.eventRender = function(event, element, view) {
    var location = ''
    if (event.location !== '') {
      location = '<i>' + event.location + '</i><br>'
    }
    element.qtip({
      content: '<b>' + event.title + '</b><br>' + location + event.description,
      show: 'click',
      hide: 'unfocus',
      position: {
        target: 'mouse',
        viewport: $(window),
        adjust: {
          mouse: false,
          method: 'flip shift'
        }
      },
      style: {
        classes: 'cal-section-info'
      },
    });
    return element
  }

  this.viewRender = function(view, element) {
    CalendarRangeService.setRange(view.start, view.end, view.type);
  }

  $scope.uiConfig = {
    calendar:{
      defaultView: 'agendaWeek',
      timezone: 'local',
      header:{
        left: 'title',
        center: '',
        right: 'agendaDay,agendaWeek,month today prev,next'
      },
      firstDay: 1,
      eventClick: $scope.alertOnEventClick,
      eventRender: $scope.eventRender,
      viewRender: this.viewRender,
    }
  };

  this.refresh = function(calendarName) {
    if(uiCalendarConfig.calendars[calendarName] !== undefined){
      uiCalendarConfig.calendars[calendarName].fullCalendar('refetchEvents');
    }
  };

  this.toggleEnabled = function(calendarPrimaryKey) {
    $http({
      method: 'GET',
      url: "/v1/gcalendars/" + calendarPrimaryKey + "/toggle-enabled/"
    }).then(function toggledSuccess(data) {}, function toggledFail(data) {
      console.log("Could not save preferences for calendar " + calendarPrimaryKey);
    });
  };

  this.eventSources = [this.events];
});
