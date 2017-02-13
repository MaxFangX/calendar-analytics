analyticsApp.component('categoryDetails', {
  templateUrl: '/static/js/components/category-details/category-details.html',
  controller: ['$scope', '$http', 'QueryService', CategoriesDetailCtrl],
  controllerAs: '$ctrl',
  bindings: {
    displayName: '@',
    categoryId: '@',
    categoryHours: '@'
  }
});

function CategoriesDetailCtrl($scope, $http, QueryService){
  var _this = this;
  this.$onInit = function () {
    var categoryId = this.categoryId;
    this.categoryUrl = '/v1/categories/' + categoryId + '/events';
    this.initialize();
  };
  var query_timezone = moment.tz.guess();
  this.categoryEvents = [];
  this.pageEvents = [];
  this.dailyData = [];
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
    QueryService.populateDay('Category day' + _this.categoryId, 'Category', _this.categoryId, []).
    then(function populate(data) {
      _this.timeStep = "day";
      var numDays = data.lineGraph[0].values.length;
      _this.averageHours = Math.round(((_this.categoryHours / numDays) * 100)) / 100;
      _this.ctrlGraphData = data.lineGraph;
      _this.showGraph(data.maxYValue);
      _this.dailyData = data;
    }, function errorCallback() {
      throw "Failed to get timeseries day";
    });
  };

  this.showWeekly = function() {
    var data = QueryService.populateData('Category week' + _this.categoryId, 'Category', _this.categoryId, "week", _this.dailyData);
    _this.timeStep = "week";
    var numWeeks = data.lineGraph[0].values.length;
    _this.averageHours = Math.round(((_this.categoryHours / numWeeks) * 100)) / 100;
    _this.ctrlGraphData = data.lineGraph;
    _this.showGraph(data.maxYValue);
  };

  this.showMonthly = function() {
    var data = QueryService.populateData('Category month' + _this.categoryId, 'Category', _this.categoryId, "month", _this.dailyData);
   _this.timeStep = "month";
   var numMonths = data.lineGraph[0].values.length;
   _this.averageHours = Math.round(((_this.categoryHours / numMonths) * 100)) / 100;
   _this.ctrlGraphData = data.lineGraph;
   _this.showGraph(data.maxYValue);
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
      url: this.categoryUrl + '.json',
      params: {
        page:pageNum
      }
    }).
    then(function successCallback(response) {
      for (var i = 0; i < response.data.results.length; i++) {
        var event = response.data.results[i];
        _this.categoryEvents.unshift({
          start: (new Date(event.start)).toString(),
          name: event.name,
        });
      }
      if (response.data.next !== null) {
        pageNum += 1;
        _this.getEvents(pageNum);
      } else {
        _this.lastPage = Math.ceil(_this.categoryEvents.length / _this.pageSize);
        _this.showPageEvents();
        _this.categoryEvents.dataLoaded = true;
      }
    }, function errorCallback() {
      throw "Failed to get events";
    });
  };

  this.initialize = function() {
    this.showDaily();
    this.getEvents(1);
  }.bind(this);
}
