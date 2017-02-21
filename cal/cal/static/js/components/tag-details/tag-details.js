analyticsApp.component('tagDetails', {
  templateUrl: '/static/js/components/tag-details/tag-details.html',
  controller: ['$scope', '$interpolate', '$http', 'CalendarFilterService', 'QueryService', 'CalendarSelect', TagsDetailCtrl],
  bindings: {
    label: '@',
    keywords: '@',
    tagId: '@'
  }
});

function TagsDetailCtrl($scope, $interpolate, $http, CalendarFilterService, QueryService, CalendarSelect ) {
  var _this = this;
  this.calendars = CalendarSelect.calendars;

  this.$onInit = function () {
    var tagId = this.tagId;
    this.tagUrl = '/v1/tags/' + tagId;
    this.tagEvent = '/v1/tags/' + tagId + '/events';
    this.categoryTags = '/v1/tags/' + tagId + '/by-category';
    this.refresh();
  };

  var query_timezone = moment.tz.guess();
  this.tagHours = 0;
  this.tagEvents = [];
  this.pageEvents = [];
  this.dailyData = [];
  this.tagEvents.dataLoaded = false;
  this.timeStep = "";
  this.currentPage = 0;
  this.pageSize = 25;
  this.lastPage = 0;

  $scope.$on('calendarFilter:updated', function(event, data) {
    _this.tagEvents.dataLoaded = false;
    _this.refresh();
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
      url: this.categoryTags + '.json',
      params: {
        calendar_ids: JSON.stringify(CalendarSelect.getEnabledCalendarIds()),
      }
    }).then(function successCallback(response) {
      _this.tagsByCategoriesData = [];
      for (var i = 0; i < response.data.length; i++) {
        var category = response.data[i];
        _this.tagsByCategoriesData.push({
          label: category[0],
          color: category[1],
          hours: category[2]
        });
      }
      _this.showCategoryPie();
    }, function errorCallback() {
      console.log("Failed to get tags by categories");
    });
  };

  this.showDaily = function() {
    QueryService.populateDay('Tag day ' + CalendarSelect.getEnabledCalendarIds() + _this.tagId, 'Tag', _this.tagId, CalendarSelect.getEnabledCalendarIds()).
    then(function populate(data) {
      _this.timeStep = "day";
      var numDays = data.lineGraph[0].values.length
      _this.averageHours = Math.round(((_this.tagHours / numDays) * 100)) / 100;
      _this.ctrlGraphData = data.lineGraph;
      _this.showGraph(data.maxYValue);
      _this.dailyData = data;
    })
  };

  this.showWeekly = function() {
    var data = QueryService.populateData('Tag week ' + CalendarSelect.getEnabledCalendarIds() + _this.tagId, 'Tag', _this.tagId, "week", _this.dailyData)
    _this.timeStep = "week";
    var numWeeks = data.lineGraph[0].values.length
    _this.averageHours = Math.round(((_this.tagHours / numWeeks) * 100)) / 100;
    _this.ctrlGraphData = data.lineGraph;
    _this.showGraph(data.maxYValue);
  };

  this.showMonthly = function() {
    var data = QueryService.populateData('Tag month ' + CalendarSelect.getEnabledCalendarIds() + _this.tagId, 'Tag', _this.tagId, "month", _this.dailyData)
    _this.timeStep = "month";
    var numMonths = data.lineGraph[0].values.length
    _this.averageHours = Math.round(((_this.tagHours / numMonths) * 100)) / 100;
    _this.ctrlGraphData = data.lineGraph;
    _this.showGraph(data.maxYValue);
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
      url: this.tagEvent + '.json',
      params: {
        page: pageNum,
        calendar_ids: JSON.stringify(CalendarSelect.getEnabledCalendarIds())
      }
    }).then(function successCallback(response) {
      _this.tagEvents = [];
      for (var i = 0; i < response.data.results.length; i++) {
        var event = response.data.results[i];
        _this.tagEvents.unshift({
          start: (new Date(event.start)).toString(),
          name: event.name,
        });
      }
      if (response.data.next !== null) {
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
      url: this.tagUrl + '.json',
      params: {
        calendar_ids: JSON.stringify(CalendarSelect.getEnabledCalendarIds()),
      }
    }).then(function successCallback(response) {
      _this.tagHours = response.data.hours;
      if (_this.timeStep === "day" || _this.timeStep === "") {
        _this.showDaily();
      }
      if (_this.timeStep === "week") {
        _this.showWeekly();
      }
      if (_this.timeStep === "month") {
        _this.showMonthly();
      }
      _this.getEvents(1);
      _this.showTagsByCategories();
    });
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
                                      CalendarSelect.getEnabledCalendarIds());
    });
  };
}
