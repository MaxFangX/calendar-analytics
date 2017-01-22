analyticsApp.component('categoryDetails', {
  templateUrl: '/static/templates/category-details.html',
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
