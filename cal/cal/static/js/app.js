/*jslint devel: true, browser: true, jquery: true */
/*global d3, moment */

var analyticsApp = window.angular.module('analyticsApp', ['analyticsApp.services', 'nvd3', 'ui.calendar']);

analyticsApp.controller('LoggedInCtrl', function LoggedInController() {
});


analyticsApp.component('tagDetails', {
  templateUrl: '/static/templates/tagDetails.html',
  controller: ['$scope', '$interpolate', '$http', 'CalendarFilterService', 'QueryService', TagsDetailCtrl],
  controllerAs: '$ctrl',
  bindings: {
    tagId: '@',
  }
});

function TagsDetailCtrl($scope, $interpolate, $http, CalendarFilterService, QueryService) {
  var _this = this;
  var tagUrl = '/v1/tags/' + this.tagId;
  var tagEvent = '/v1/tags/' + this.tagId + '/events';
  var timeseriesWeek = '/v1/tags/' + this.tagId + '/timeseries/week';
  var timeseriesMonth = '/v1/tags/' + this.tagId + '/timeseries/month';
  var timeseriesDay = '/v1/tags/' + this.tagId + '/timeseries/day';
  var categoryTags = '/v1/tags/' + this.tagId + '/by-category';
  var query_timezone = moment.tz.guess();
  var calendarIds = [];
  this.tagHours = 0;
  this.tagEvents = [];
  this.pageEvents = [];
  this.tagEvents.dataLoaded = false;
  this.timeStep = "";
  this.currentPage = 0;
  this.pageSize = 25;
  this.lastPage = 0;

  $scope.$on('calendarFilter:updated', function(event, data) {
    _this.tagEvents.dataLoaded = false;
    var filterData = CalendarFilterService.getFilter();
    calendarIds = filterData.calendarIds;
    if (filterData.calendarIds.length > 0) {
      _this.refresh();
    }
  });

  // Refreshes the line graph
  this.showGraph = function(maxYValue) {
    // line graph
    this.tagLine = {
      chart: {
        type: 'lineChart',
        height: 415,
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
        interpolate: 'cardinal'
      },
    };
  }.bind(this);

  this.showCategoryPie = function() {
    this.categoryPie = {
      chart: {
        type: 'pieChart',
        height: 200,
        x: function(d){return d.label;},
        y: function(d){return d.hours;},
        showLabels: false,
        growOnHover: true,
        duration: 500,
        labelThreshold: 0.01,
        labelSunbeamLayout: true,
        showLegend: false
      },
    };
  };

  this.showTagsByCategories = function() {
    $http({
      method: 'GET',
      url: categoryTags + '.json',
    }).success(function successCallback(data) {
      _this.tagsByCategoriesData = [];
      for (var i = 0; i < data.length; i++) {
        var category = data[i];
        _this.tagsByCategoriesData.push({
          label: category[0],
          color: category[1],
          hours: category[2]
        });
      }
      _this.showCategoryPie();
    });
  };

  this.showDaily = function() {
    $http({
      method: 'GET',
      url: timeseriesDay + '.json',
      params: {
        timezone: query_timezone,
        calendar_ids: JSON.stringify(calendarIds),
      }
    }).
    success(function successCallback(data) {
      _this.timeStep = "day";
      // round(... * 100) / 100 necessary to round average hours to two decimal
      _this.averageHours = Math.round(((_this.tagHours / data[0].length) * 100)) / 100;
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
        calendar_ids: JSON.stringify(calendarIds),
      }
    }).
    success(function successCallback(data) {
      _this.timeStep = "week";
      // round(... * 100) / 100 necessary to round average hours to two decimal
      _this.averageHours = Math.round(((_this.tagHours / data[0].length) * 100)) / 100;
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
        calendar_ids: JSON.stringify(calendarIds),
      }
    }).
    success(function successCallback(data) {
      _this.timeStep = "month";
      _this.averageHours = Math.round(((_this.tagHours / data[0].length) * 100)) / 100;
      var eventData = QueryService.populateData(data, 'Tag');
      _this.ctrlGraphData = eventData[0];
      _this.showGraph(eventData[1]);
    });
  };

  this.showPageEvents = function() {
    var start = this.currentPage * this.pageSize;
    var end = (start + this.pageSize > this.tagEvents.length) ? this.tagEvents.length : start + this.pageSize;
    this.pageEvents = [];
    for (var i = start; i < end; i++) {
      this.pageEvents.push(_this.tagEvents[i]);
    }
  }.bind(this);

  this.getEvents = function(pageNum) {
    $http({
      method: 'GET',
      url: tagEvent + '.json',
      params: {
        page: pageNum,
        calendar_ids: JSON.stringify(calendarIds)
      }
    }).
    success(function successCallback(data) {
      _this.tagEvents = [];
      for (var i = 0; i < data.results.length; i++) {
        var event = data.results[i];
        _this.tagEvents.unshift({
          start: (new Date(event.start)).toString(),
          name: event.name,
        });
      }
      if (data.next !== null) {
        pageNum += 1;
        _this.getEvents(pageNum);
      } else {
        _this.lastPage = Math.ceil(_this.tagEvents.length / _this.pageSize);
        _this.showPageEvents();
        _this.tagEvents.dataLoaded = true;
      }
    });
  };

  this.refresh = function() {
    $http({
      method: 'GET',
      url: tagUrl + '.json',
      params: {
        calendar_ids: JSON.stringify(calendarIds),
      }
    }).
    success(function successCallback(data) {
      _this.tagHours = data.hours;
      if (_this.timeStep === "day") {
        _this.showDaily();
      }
      if (_this.timeStep === "week" || _this.timeStep === "") {
        _this.showWeekly();
      }
      if (_this.timeStep === "month") {
        _this.showMonthly();
      }
      _this.getEvents(1);
      _this.showTagsByCategories();
    });
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

function CategoryListCtrl($scope, $http, CalendarFilterService, CategoryService) {

  var _this = this;

  this.categories = [];
  this.categories.dataLoaded = false;

  $scope.$on('calendarFilter:updated', function(event, data) {
    /* jshint unused:vars */
    _this.categories.dataLoaded = false;
    var filterData = CalendarFilterService.getFilter();
    if (!_this.isCumulative) {
      CategoryService.getCategories(filterData.filterKey, filterData.start,
        filterData.end, filterData.calendarIds)
        .then(function(categories) {
          _this.categories = categories;
          _this.filterKey = filterData.filterKey;
          _this.categories.dataLoaded = true;
        });
    } else {
      CategoryService.getCategories('cumulative ' + filterData.filterKey, null,
        null, filterData.calendarIds)
        .then(function(categories) {
          _this.categories = categories;
          _this.categories.dataLoaded = true;
        });
    }
  });

  this.hideZeroHoursFilter = function(value, index, array) {
    /* jshint unused:vars */
    return !(_this.hideZeroHours && value.hours === 0);
  };

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
      height: 200,
      x: function(d){return d.label;},
      y: function(d){return d.hours;},
      showLabels: false,
      growOnHover: true,
      duration: 500,
      labelThreshold: 0.01,
      labelSunbeamLayout: true,
      showLegend: false
    },
  };
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

function CategoriesDetailCtrl($scope, $http, QueryService){
  var _this = this;
  var categoryUrl = '/v1/categories/' + this.categoryId + '/events';
  var timeseriesWeek = '/v1/categories/' + this.categoryId + '/timeseries/week';
  var timeseriesMonth = '/v1/categories/' + this.categoryId + '/timeseries/month';
  var timeseriesDay = '/v1/categories/' + this.categoryId + '/timeseries/day';
  var query_timezone = moment.tz.guess();
  this.categoryEvents = [];
  this.pageEvents = [];
  this.categoryEvents.dataLoaded = false;
  this.timeStep = "";
  this.currentPage = 0;
  this.pageSize = 25;
  this.lastPage = 0;

  // line graph
  this.showGraph = function(maxYValue) {
    this.categoryLine = {
      chart: {
        type: 'lineChart',
        height: 300,
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
        interpolate: 'cardinal',
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
      _this.averageHours = Math.round(((_this.categoryHours / data[0].length) * 100)) / 100;
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
      _this.averageHours = Math.round(((_this.categoryHours / data[0].length) * 100)) / 100;
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
      _this.averageHours = Math.round(((_this.categoryHours / data[0].length) * 100)) / 100;
      var eventData = QueryService.populateData(data, 'Category');
      _this.ctrlGraphData = eventData[0];
      _this.showGraph(eventData[1]);
    });
  };

  this.showPageEvents = function() {
    var start = this.currentPage * this.pageSize;
    var end = (start + this.pageSize > this.categoryEvents.length) ? this.categoryEvents.length : start + this.pageSize;
    this.pageEvents = [];
    for (var i = start; i < end; i++) {
      this.pageEvents.push(_this.categoryEvents[i]);
    }
  }.bind(this);

  this.getEvents = function(pageNum) {
    $http({
      method: 'GET',
      url: categoryUrl + '.json',
      params: {
        page:pageNum
      }
    }).
    success(function successCallback(data) {
      for (var i = 0; i < data.results.length; i++) {
        var event = data.results[i];
        _this.categoryEvents.unshift({
          start: (new Date(event.start)).toString(),
          name: event.name,
        });
      }
      if (data.next !== null) {
        pageNum += 1;
        _this.getEvents(pageNum);
      } else {
        _this.lastPage = Math.ceil(_this.categoryEvents.length / _this.pageSize);
        _this.showPageEvents();
        _this.categoryEvents.dataLoaded = true;
      }
    });
  };

  this.initialize = function() {
    this.showWeekly();
    this.getEvents(1);
  }.bind(this);

  this.initialize();
}
