/*jslint devel: true, browser: true, jquery: true */
/*global d3, moment */

var analyticsApp = window.angular.module('analyticsApp', ['analyticsApp.services', 'nvd3', 'ui.calendar']);

analyticsApp.controller('LoggedInCtrl', function LoggedInController() {
});

function TagListCtrl($scope, $http, CalendarRangeService, TagService) {

  var _this = this;

  this.tags = [];

  $scope.$on('calendarRange:updated', function(event, data) {
    /* jshint unused:vars */
    var rangeData = CalendarRangeService.getRange();
    if (!_this.isCumulative) {
      TagService.getTags(rangeData.timeRange, rangeData.start, rangeData.end)
        .then(function(tags) {
          _this.tags = tags;
          _this.timeRange = rangeData.timeRange;
        });
    }
  });

  // Initialization
  this.initialize = function() {
    var tagsPromise;
    if (this.isCumulative) {
      tagsPromise = TagService.getTags('cumulative', null, null);
    } else {
      var initialTimeRange = CalendarRangeService.getRange();
      tagsPromise = TagService.getTags(initialTimeRange.timeRange, initialTimeRange.start, initialTimeRange.end);
    }
    tagsPromise.then(function(tags) {
      _this.tags = tags;
    });
  }.bind(this);

  this.initialize();

  this.hideZeroHoursFilter = function (value, index, array) {
    /* jshint unused:vars */
    if (this.hideZeroHours && value.hours === 0) {
      return false;
    } else {
      return true;
    }
  }.bind(this);

  this.create = function(tag) {
    TagService.createTag(tag.label, tag.keywords)
      .success(function addToList(data) {
        _this.tags.push({
          id: data.id,
          label: data.label,
          keywords: data.keywords,
          hours: data.hours,
          editing: false
        });
      });
  }.bind(this);

  this.startEdit = function(tagId) {
    var tag = this.tags.find(function(tag, index, array) {
      /* jshint unused:vars */
      return tag.id == tagId;
    });
    tag.newLabel = tag.label;
    tag.newKeywords = tag.keywords;
    tag.editing = true;
  };

  this.submitEdit = function(tagId) {
    var tag = this.tags.find(function(tag, index, array) {
      /* jshint unused:vars */
      return tag.id == tagId;
    });
    tag.editing = false;
    TagService.editTag(tagId, tag.newLabel, tag.newKeywords)
      .then(function(returnedTag) {
        tag.label = returnedTag.label;
        tag.keywords = returnedTag.keywords;
        tag.hours = returnedTag.hours;
      });
  }.bind(this);

  this.cancelEdit = function(tagId) {
    var tag = this.tags.find(function(tag, index, array) {
      /* jshint unused:vars */
      return tag.id == tagId;
    });
    tag.editing = false;
  }.bind(this);

  this.delete = function(tagId) {
    TagService.deleteTag(tagId)
      .success(function removeFromList() {
        _this.tags = _this.tags.filter(function(tag) {
          return tag.id !== tagId;
        });
      });
  };
}

analyticsApp.component('tagList', {
  templateUrl: '/static/templates/tag-list.html',
  controller: ['$scope', '$http', 'CalendarRangeService', 'TagService', TagListCtrl],
  controllerAs: '$ctrl',
  bindings: {
    isCumulative: '<?',
    displayName: '@',
    hideZeroHours: '<?'
  }
});

function TimelineBaseCtrl($scope, $http) {
  $scope.basePopulateData = function(data, type) {
    var maxYValue = 0;
    var events = []
    for (var i = 0; i < data.length; i++) {
      var event = data[i];
      var date = new Date(event[0])
      var hours = event[1]
      if (hours > maxYValue) {
        maxYValue = hours
      };
      events.push({
        x: date,
        y: hours
      });
    };
    $scope.ctrlDetails = []
    $scope.ctrlDetails.push({
      values: events,
      key: type + ' Graph',
      color: '#003057',
      strokeWidth: 2,
    });
    return [events, maxYValue];
  };
};

function TagsDetailCtrl($scope, $http) {
  var tagUrl = '/v1/tags/' + this.tagId + '/events';
  var eventWeek = '/v1/tags/' + this.tagId + '/eventWeek';
  var eventMonth = '/v1/tags/' + this.tagId + '/eventMonth';
  var eventDay = '/v1/tags/' + this.tagId + '/eventDay';
  var query_timezone = moment.tz.guess();
  $scope.tagDetails = [];
  $scope.tagEvents = [];
  $scope.tagHours = this.tagHours;

  $http({method: 'GET', url: tagUrl + '.json' }).
  success(function successCallback(data) {
    for (var i = 0; i < data.results.length; i++) {
      var event = data.results[i];
      $scope.tagEvents.push({
        start: (new Date(event.start)).toString(),
        name: event.name,
      });
    }
  });

  TimelineBaseCtrl.call(this, $scope, $http);

  $scope.populateData = function(data, type) {
    return this.basePopulateData(data, type);
  };

  // Refreshes the line graph
  $scope.showGraph = function(maxYValue) {
    // line graph
    $scope.tagLine = {
      chart: {
        type: 'lineChart',
        height: 450,
        margin : {
          top: 20,
          right: 20,
          bottom: 40,
          left: 55
        },
        x: function(d){ return d.x; },
        y: function(d){ return d.y; },
        useInteractiveGuideline: true,
        xScale: d3.time.scale(),
        xAxis: {
          axisLabel: 'Date',
          tickFormat: function(d) {
                          return d3.time.format('%m/%d/%y')(d)
                      }
        },
        yAxis: {
          axisLabel: 'Hours',
          tickFormat: function(d){
            return d3.format('.02f')(d);
          },
          axisLabelDistance: -10,
        },
        forceY: [0, maxYValue+1],
      },
    };
  };

  $scope.showDaily = function() {
    $http({
      method: 'GET',
      url: eventDay + '.json',
      params: {
        timezone: query_timezone,
      }
    }).
    success(function successCallback(data) {
      var eventData = $scope.populateData(data, 'Tag');
      $scope.showGraph(eventData[1]);
    });
  };

  $scope.showWeekly = function() {
    $http({
      method: 'GET',
      url: eventWeek + '.json',
      params: {
        timezone: query_timezone,
      }
    }).
    success(function successCallback(data) {
      var eventData = $scope.populateData(data, 'Tag');
      $scope.showGraph(eventData[1]);
    });
  };

  $scope.showMonthly = function() {
    $http({
      method: 'GET',
      url: eventMonth + '.json',
      params: {
        timezone: query_timezone,
      }
    }).
    success(function successCallback(data) {
      var eventData = $scope.populateData(data, 'Tag');
      $scope.showGraph(eventData[1]);
    });
  };

  // Initial load of weekly data
  $scope.showWeekly();
};


analyticsApp.component('tagDetails', {
  templateUrl: '/static/templates/tagDetails.html',
  controller: TagsDetailCtrl,
  controllerAs: '$ctrl',
  bindings: {
    tagId: '@',
    tagHours: '@'
  }
});

function CategoryListCtrl($scope, $http, CalendarRangeService, CategoryService) {

  var _this = this;

  this.categories = [];
  this.categories.dataLoaded = false;

  $scope.$on('calendarRange:updated', function(event, data) {
    /* jshint unused:vars */
    var rangeData = CalendarRangeService.getRange();
    if (!_this.isCumulative) {
      CategoryService.getCategories(rangeData.timeRange, rangeData.start, rangeData.end)
        .then(function(categories) {
          _this.categories = categories;
          _this.timeRange = rangeData.timeRange;
          _this.categories.dataLoaded = true;
        });
    }
  });

  // Initialization
  this.initialize = function() {

    var categoriesPromise;

    if (this.isCumulative) {
      categoriesPromise = CategoryService.getCategories('cumulative', null, null);
    } else {
      var initialTimeRange = CalendarRangeService.getRange();
      categoriesPromise = CategoryService.getCategories(initialTimeRange.timeRange, initialTimeRange.start, initialTimeRange.end);
      _this.timeRange = initialTimeRange.timeRange;
    }
    categoriesPromise.then(function(categories) {
      _this.categories = categories;
      _this.categories.dataLoaded = true;
    });
  }.bind(this);
  this.initialize();

  this.hideZeroHoursFilter = function (value, index, array) {
    /* jshint unused:vars */
    if (this.hideZeroHours && value.hours === 0) {
      return false;
    } else {
      return true;
    }
  }.bind(this);

  this.startEdit = function(categoryId) {
    var category = _this.categories.find(function(category, index, array) {
      /* jshint unused:vars */
      return category.id == categoryId;
    });
    category.newLabel = category.label;
    category.editing = true;
  };

  this.submitEdit = function(categoryId) {
    var category = _this.categories.find(function(category, index, array) {
      /* jshint unused:vars */
      return category.id == categoryId;
    });
    category.editing = false;

    CategoryService.editCategory(categoryId, category.newLabel)
      .then(function(returnedCategory) {
        category.label = returnedCategory.label;
        category.hours = returnedCategory.hours;
      });
  };

  this.cancelEdit = function(categoryId) {
    var category = this.categories.find(function(category, index, array) {
      /* jshint unused:vars */
      return category.id == categoryId;
    });
    category.editing = false;
  }.bind(this);

  this.delete = function(categoryId) {
    CategoryService.deleteCategory(categoryId)
      .success(function removeFromList(data) {
        /* jshint unused:vars */
        _this.categories = _this.categories.filter(function(category) {
          return category.id !== categoryId;
        });
      });
  };

  // categories pie chart
  this.categoryPie = {
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
}

analyticsApp.component('categoryList', {
  templateUrl: '/static/templates/category-list.html',
  controller: ['$scope', '$http', 'CalendarRangeService', 'CategoryService', CategoryListCtrl],
  controllerAs: '$ctrl',
  bindings: {
    isCumulative: '<?',
    displayName: '@',
    hideZeroHours: '<?'
  }
});

function CategoriesDetailCtrl($scope, $http){
  var categoryUrl = '/v1/colorcategories/' + this.categoryId + '/events';
  var eventWeek = '/v1/colorcategories/' + this.categoryId + '/eventWeek';
  var eventMonth = '/v1/colorcategories/' + this.categoryId + '/eventMonth';
  var eventDay = '/v1/colorcategories/' + this.categoryId + '/eventDay';
  var query_timezone = moment.tz.guess();
  $scope.categoryDetails = [];
  $scope.categoryEvents = [];
  $scope.categoryHours = this.categoryHours;

  $http({method: 'GET', url: categoryUrl + '.json' }).
  success(function successCallback(data) {
    for (var i = 0; i < data.results.length; i++) {
      var event = data.results[i];
      $scope.categoryEvents.push({
        start: (new Date(event.start)).toString(),
        name: event.name,
      });
    }
  });

  TimelineBaseCtrl.call(this, $scope, $http);

  $scope.populateData = function(data, type) {
    return this.basePopulateData(data, type);
  };

  // line graph
  $scope.showGraph = function(maxYValue) {
    $scope.categoryLine = {
      chart: {
        type: 'lineChart',
        height: 450,
        margin : {
          top: 20,
          right: 20,
          bottom: 40,
          left: 55
        },
        x: function(d){ return d.x; },
        y: function(d){ return d.y; },
        useInteractiveGuideline: true,
        xScale: d3.time.scale(),
        xAxis: {
          axisLabel: 'Date',
          tickFormat: function(d) {
                          return d3.time.format('%m/%d/%y')(d)
                      }
        },
        yAxis: {
          axisLabel: 'Hours',
          tickFormat: function(d){
            return d3.format('.02f')(d);
          },
          axisLabelDistance: -10
        },
        forceY: [0, maxYValue+1],
      },
    };
  };

  $scope.showDaily = function() {
    $http({
      method: 'GET',
      url: eventDay + '.json',
      params: {
        timezone: query_timezone,
      }
    }).
    success(function successCallback(data) {
      var eventData = $scope.populateData(data, 'Category');
      $scope.showGraph(eventData[1]);
    });
  };

  $scope.showWeekly = function() {
    $http({
      method: 'GET',
      url: eventWeek + '.json',
      params: {
        timezone: query_timezone,
      }
    }).
    success(function successCallback(data) {
      var eventData = $scope.populateData(data, 'Category');
      $scope.showGraph(eventData[1]);
    });
  };

  $scope.showMonthly = function() {
    $http({
      method: 'GET',
      url: eventMonth + '.json',
      params: {
        timezone: query_timezone,
      }
    }).
    success(function successCallback(data) {
      var eventData = $scope.populateData(data, 'Category');
      $scope.showGraph(eventData[1]);
    });
  };

  // Initial load of weekly data
  $scope.showWeekly();
};

analyticsApp.component('categoryDetails', {
  templateUrl: '/static/templates/categoryDetails.html',
  controller: CategoriesDetailCtrl,
  controllerAs: '$ctrl',
  bindings: {
    categoryId: '@',
    categoryHours: '@'
  }
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
    /* jshint unused:vars */
    var location = '';
    if (event.location !== '') {
      location = '<i>' + event.location + '</i><br>';
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
    return element;
  };

  this.viewRender = function(view, element) {
    /* jshint unused:vars */
    CalendarRangeService.setRange(view.start, view.end, view.type);
  };

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
    }).then(
      function toggledSuccess(data) {/* jshint unused:vars */},
      function toggledFail(data) {
        /* jshint unused:vars */
        console.log("Could not save preferences for calendar " + calendarPrimaryKey);
      });
  };

  this.eventSources = [this.events];
});
