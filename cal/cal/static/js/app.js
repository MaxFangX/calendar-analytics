/*jslint devel: true, browser: true, jquery: true */
/*global d3, moment */

var analyticsApp = window.angular.module('analyticsApp', ['analyticsApp.services', 'nvd3', 'ui.calendar']);

analyticsApp.controller('LoggedInCtrl', function LoggedInController() {
});

function TagListCtrl($scope, $http, CalendarFilterService, TagService) {

  var _this = this;

  this.tags = [];
  this.tags.dataLoaded = false;

  $scope.$on('calendarFilter:updated', function(event, data) {
    /* jshint unused:vars */
    var filterData = CalendarFilterService.getFilter();
    if (!this.isCumulative) {
      TagService.getTags(filterData.filterKey, filterData.start, filterData.end,
                         filterData.calendarIds)
        .then(function(tags) {
          this.tags = tags;
          this.filterKey = filterData.filterKey;
          this.tags.dataLoaded = true;
        });
      }
  }.bind(this));

  // Initialization
  this.initialize = function() {
    var tagsPromise;
    var initialFilterData = CalendarFilterService.getFilter();
    if (this.isCumulative) {
      tagsPromise = TagService.getTags('cumulative', null, null,
        initialFilterData.calendarIds);
    } else {
      tagsPromise = TagService.getTags(initialFilterData.filterKey,
        initialFilterData.start, initialFilterData.end,
        initialFilterData.calendarIds);
    }
    tagsPromise.then(function(tags) {
      _this.tags = tags;
      _this.tags.dataLoaded = true;
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
      _this.tags.dataLoaded = true;
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
        _this.tags.dataLoaded = true;
      });
  };
}

analyticsApp.component('tagList', {
  templateUrl: '/static/templates/tag-list.html',
  controller: ['$scope', '$http', 'CalendarFilterService', 'TagService', TagListCtrl],
  controllerAs: '$ctrl',
  bindings: {
    isCumulative: '<?',
    displayName: '@',
    hideZeroHours: '<?'
  }
});

function TagsDetailCtrl($scope, $interpolate, $http, QueryService) {
  var _this = this;
  var tagUrl = '/v1/tags/' + this.tagId + '/events';
  var timeseriesWeek = '/v1/tags/' + this.tagId + '/timeseries/week';
  var timeseriesMonth = '/v1/tags/' + this.tagId + '/timeseries/month';
  var timeseriesDay = '/v1/tags/' + this.tagId + '/timeseries/day';
  var query_timezone = moment.tz.guess();
  this.tagEvents = [];
  this.tagEvents.dataLoaded = false;
  this.averageHours = 0;
  this.timeStep = "";

  // Refreshes the line graph
  this.showGraph = function(maxYValue) {
    // line graph
    _this.tagLine = {
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
        xScale: d3.time.scale(),
        xAxis: {
          axisLabel: 'Date',
          tickFormat: function(d) {
            return d3.time.format('%m/%d/%y')(d);
          },
        },
        yAxis: {
          axisLabel: 'Hours',
          tickFormat: function(d){
            return d3.format('.02f')(d);
          },
          axisLabelDistance: -10,
        },
        forceY: [0, maxYValue + 1],
      },
    };
  }.bind(this);

  this.showDaily = function() {
    $http({
      method: 'GET',
      url: timeseriesDay + '.json',
      params: {
        timezone: query_timezone,
      }
    }).
    success(function successCallback(data) {
      _this.timeStep = "day";
      // round(... * 100) / 100 necessary to round average hours to two decimal
      _this.averageHours = Math.round(((_this.tagHours / data.length) * 100)) / 100;
      var eventData = QueryService.populateData(data, 'Tag');
      _this.ctrlGraphData = eventData[0];
      _this.showGraph(eventData[1]);
    });
  };

  this.showWeekly = function() {
    $http({
      method: 'GET',
      url: timeseriesWeek + '.json',
      params: {
        timezone: query_timezone,
      }
    }).
    success(function successCallback(data) {
      _this.timeStep = "week";
      // round(... * 100) / 100 necessary to round average hours to two decimal
      _this.averageHours = Math.round(((_this.tagHours / data.length) * 100)) / 100;
      var eventData = QueryService.populateData(data, 'Tag');
      _this.ctrlGraphData = eventData[0];
      _this.showGraph(eventData[1]);
    });
  };

  this.showMonthly = function() {
    $http({
      method: 'GET',
      url: timeseriesMonth + '.json',
      params: {
        timezone: query_timezone,
      }
    }).
    success(function successCallback(data) {
      _this.timeStep = "month";
      _this.averageHours = Math.round(((_this.tagHours / data.length) * 100)) / 100;
      var eventData = QueryService.populateData(data, 'Tag');
      _this.ctrlGraphData = eventData[0];
      _this.showGraph(eventData[1]);
    });
  };

  this.initialize = function() {
    this.showWeekly();
    $http({method: 'GET', url: tagUrl + '.json' }).
    success(function successCallback(data) {
      for (var i = 0; i < data.results.length; i++) {
        var event = data.results[i];
        _this.tagEvents.unshift({
          start: (new Date(event.start)).toString(),
          name: event.name,
        });
      }
      _this.tagEvents.dataLoaded = true;
    });
  }.bind(this);
  this.initialize();
}


analyticsApp.component('tagDetails', {
  templateUrl: '/static/templates/tagDetails.html',
  controller: ['$scope', '$interpolate', '$http', 'QueryService', TagsDetailCtrl],
  controllerAs: '$ctrl',
  bindings: {
    tagId: '@',
    tagHours: '@'
  }
});

function CategoryListCtrl($scope, $http, CalendarFilterService, CategoryService) {

  var _this = this;

  this.categories = [];
  this.categories.dataLoaded = false;

  $scope.$on('calendarFilter:updated', function(event, data) {
    /* jshint unused:vars */
    var filterData = CalendarFilterService.getFilter();
    if (!_this.isCumulative) {
      CategoryService.getCategories(filterData.filterKey, filterData.start,
        filterData.end, filterData.calendarIds)
        .then(function(categories) {
          _this.categories = categories;
          _this.filterKey = filterData.filterKey;
          _this.categories.dataLoaded = true;
        });
    }
  });

  // Initialization
  this.initialize = function() {

    var categoriesPromise;
    var initialFilterData = CalendarFilterService.getFilter();
    if (this.isCumulative) {
      categoriesPromise = CategoryService.getCategories('cumulative', null,
        null, initialFilterData.calendarIds);
    } else {
      categoriesPromise = CategoryService.getCategories(
        initialFilterData.filterKey,
        initialFilterData.start,
        initialFilterData.end,
        initialFilterData.calendarIds
      );
      _this.filterKey = initialFilterData.filterKey;
    }
    categoriesPromise.then(function(categories) {
      _this.categories = categories;
      _this.categories.dataLoaded = true;
    });
  }.bind(this);
  this.initialize();

  this.hideZeroHoursFilter = function(value, index, array) {
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
        _this.categories.dataLoaded = true;
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
      _this.categories.dataLoaded = true;
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
  controller: ['$scope', '$http', 'CalendarFilterService', 'CategoryService', CategoryListCtrl],
  controllerAs: '$ctrl',
  bindings: {
    isCumulative: '<?',
    displayName: '@',
    hideZeroHours: '<?'
  }
});

function CategoriesDetailCtrl($scope, $http, QueryService){
  var _this = this;
  var categoryUrl = '/v1/categories/' + this.categoryId + '/events';
  var timeseriesWeek = '/v1/categories/' + this.categoryId + '/timeseries/week';
  var timeseriesMonth = '/v1/categories/' + this.categoryId + '/timeseries/month';
  var timeseriesDay = '/v1/categories/' + this.categoryId + '/timeseries/day';
  var query_timezone = moment.tz.guess();
  this.categoryEvents = [];
  this.categoryEvents.dataLoaded = false;
  this.averageHours = 0;
  this.timeStep = "";

  // line graph
  this.showGraph = function(maxYValue) {
    this.categoryLine = {
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
        xScale: d3.time.scale(),
        xAxis: {
          axisLabel: 'Date',
          tickFormat: function(d) {
            return d3.time.format('%m/%d/%y')(d);
          },
        },
        yAxis: {
          axisLabel: 'Hours',
          tickFormat: function(d){
            return d3.format('.02f')(d);
          },
          axisLabelDistance: -10
        },
        forceY: [0, maxYValue + 1],
      },
    };
  }.bind(this);

  this.showDaily = function() {
    $http({
      method: 'GET',
      url: timeseriesDay + '.json',
      params: {
        timezone: query_timezone,
      }
    }).
    success(function successCallback(data) {
      _this.timeStep = "day";
      _this.averageHours = Math.round(((_this.categoryHours / data.length) * 100)) / 100;
      var eventData = QueryService.populateData(data, 'Category');
      _this.ctrlGraphData = eventData[0];
      _this.showGraph(eventData[1]);
    });
  };

  this.showWeekly = function() {
    $http({
      method: 'GET',
      url: timeseriesWeek + '.json',
      params: {
        timezone: query_timezone,
      }
    }).
    success(function successCallback(data) {
      _this.timeStep = "week";
      // round(... * 100) / 100 neceessary to round average hours to two decimal
      _this.averageHours = Math.round(((_this.categoryHours / data.length) * 100)) / 100;
      var eventData = QueryService.populateData(data, 'Category');
      _this.ctrlGraphData = eventData[0];
      _this.showGraph(eventData[1]);
    });
  };

  this.showMonthly = function() {
    $http({
      method: 'GET',
      url: timeseriesMonth + '.json',
      params: {
        timezone: query_timezone,
      }
    }).
    success(function successCallback(data) {
      _this.timeStep = "month";
      _this.averageHours = Math.round(((_this.categoryHours / data.length) * 100)) / 100;
      var eventData = QueryService.populateData(data, 'Category');
      _this.ctrlGraphData = eventData[0];
      _this.showGraph(eventData[1]);
    });
  };

  this.initialize = function() {
    this.showWeekly();
    $http({method: 'GET', url: categoryUrl + '.json' }).
    success(function successCallback(data) {
      for (var i = 0; i < data.results.length; i++) {
        var event = data.results[i];
        _this.categoryEvents.unshift({
          start: (new Date(event.start)).toString(),
          name: event.name,
        });
      }
      _this.categoryEvents.dataLoaded = true;
    });
  }.bind(this);

  this.initialize();
}

analyticsApp.component('categoryDetails', {
  templateUrl: '/static/templates/categoryDetails.html',
  controller: ['$scope', '$http', 'QueryService', CategoriesDetailCtrl],
  controllerAs: '$ctrl',
  bindings: {
    categoryId: '@',
    categoryHours: '@'
  }
});

analyticsApp.controller('CalendarCtrl', function CalendarCtrl($scope, $http, $q, uiCalendarConfig, CalendarFilterService) {

  this.calendars = {};
  var _this = this;

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

      // Initialize cached calendars
      for (var i = 0; i < response.data.results.length; i++) {
        var gcal = response.data.results[i];
        if (_this.calendars[gcal.calendar_id] === undefined) {
          _this.calendars[gcal.calendar_id] = gcal;
          _this.calendars[gcal.calendar_id].enabled = gcal.enabled_by_default;
        }
      }

      // Trigger first CalendarFilter now that this.calendars has been set
      CalendarFilterService.setFilter(start, end,
        _this.getEnabledCalendarIds());

      var calendarIds = response.data.results.map(function(cal) {
        return cal.calendar_id;
      }).sort();

      $http({
        method: 'GET',
        url: "/v1/gevents.json",
        cache: true,
        params: {
          calendarIds: JSON.stringify(calendarIds),
          start: start.toISOString(),
          end: end.toISOString(),
          timezone: query_timezone,
          edge: 'truncated'
        },
      }).then(function eventSuccess(response) {
        var events = [];
        for (i = 0; i < response.data.results.length; i++) {
          var gevent = response.data.results[i];
          if (_this.calendars[gevent.calendar.calendar_id].enabled) {
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
          }
        }

        callback(events);

      }, function eventError(response) {
        console.log("Ajax call to gevents failed:");
        console.log(response);
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
    // The first time viewRender is called, the GCalendars haven't been
    // populated yet.
    if(_this.calendars.length !== 0) {
      CalendarFilterService.setFilter(view.start, view.end,
                                      this.getEnabledCalendarIds());
    }
  }.bind(this);

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

  this.toggleEnabled = function(calendarPrimaryKey) {
    $http({
      method: 'GET',
      url: "/v1/gcalendars/" + calendarPrimaryKey + "/toggle-enabled/"
    }).then(
      function toggledSuccess(data) {
        /* jshint unused:vars */
      },
      function toggledFail(data) {
        /* jshint unused:vars */
        console.log("Could not save preferences for calendar " + calendarPrimaryKey);
      }
    ).then(function() {
      CalendarFilterService.setFilter(null,
                                      null,
                                      _this.getEnabledCalendarIds());
    });
  };

  this.eventSources = [this.events];
});
