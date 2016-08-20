var analyticsApp = angular.module('analyticsApp', ['nvd3']);

// Test controller for logging in
analyticsApp.controller('LoggedInController', function LoggedInController($scope) {

  $scope.testString = "hello angular 1.5!";

});

// Controller to generate graph data from chart directive, cumulative tags
analyticsApp.controller('TagsController', function($scope, $http){
  var url = '/v1/tags';

  $http({ method: 'GET', url: url }).
    success(function (data) {
      // set the data
      $scope.data = [];
      for (var i = 0; i < data.results.length; i++) {
        var tag = data.results[i];
        $scope.data.push( {
          category: tag.label,
          hours: tag.hours
        });
      }
    });

  $scope.options = {
    chart: {
      type: 'pieChart',
      height: 500,
      x: function(d){return d.category;},
      y: function(d){return d.hours;},
      showLabels: true,
      duration: 500,
      labelThreshold: 0.01,
      labelSunbeamLayout: false,
      legend: {
        margin: {
          top: 5,
          right: 35,
          bottom: 5,
          left: 0
        }
      }
    },
    title: {
      enable: true,
      text: 'Total Hours Spent from Tags'
    },
  };
});

// Example line graph in categories, line graph per week
analyticsApp.controller('CategoriesController', function($scope){
  $scope.options = {
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
    dispatch: {
      stateChange: function(e){ console.log("stateChange"); },
      changeState: function(e){ console.log("changeState"); },
      tooltipShow: function(e){ console.log("tooltipShow"); },
      tooltipHide: function(e){ console.log("tooltipHide"); }
    },
    xAxis: {
      axisLabel: 'Categories',
      tickFormat: function(d){
          return d3.time.format('%b %d')(new Date(d));
      },
    },
    yAxis: {
      axisLabel: 'Time (hours)',
      tickFormat: function(d){
          return d3.format('.02f')(d);
      },
      axisLabelDistance: -10
    },
    // callback: function(chart){
    //   console.log("!!! lineChart callback !!!");
    // }
    },
    title: {
      enable: true,
      text: 'Categories - Last Week'
    },
  };

  // $scope.data = sinAndCos();
  $scope.data = [
    {
      values: [
        {x: new Date(2016, 5, 15), y: 4.5},
        {x: new Date(2016, 5, 22), y: 0},
        {x: new Date(2016, 5, 29), y: 5},
        {x: new Date(2016, 6, 5), y: 9.25},
      ],
      key: 'Learning',
      color: '#ff7f0e'
    },
    {
      values: [
        {x: new Date(2016, 5, 15), y: 55.25},
        {x: new Date(2016, 5, 25), y: 62.26},
        {x: new Date(2016, 5, 29), y: 57},
        {x: new Date(2016, 6, 5), y: 52.25},
      ],
      key: 'Sleeping',
      color: '#2ca02c'
    },
    {
      values: [
        {x: new Date(2016, 5, 15), y: 4.25},
        {x: new Date(2016, 5, 25), y: 0},
        {x: new Date(2016, 5, 29), y: 0.5},
        {x: new Date(2016, 6, 5), y: 40.25},
      ],
      key: 'Working',
      color: '#7777ff'
    }
  ];



  /*Random Data Generator */
  function sinAndCos() {
    var sin = [],sin2 = [], cos = [];

    // Data is represented as an array of {x,y} pairs.
    for (var i = 0; i < 100; i++) {
      sin.push({x: i, y: Math.sin(i/10)});
      sin2.push({x: i, y: i % 10 == 5 ? null : Math.sin(i/10) *0.25 + 0.5});
      cos.push({x: i, y: 0.5 * Math.cos(i/10+ 2) + Math.random() / 10});
    }

    // Line chart data should be sent as an array of series objects.
    return [
      {
        values: sin,      //values - represents the array of {x,y} data points
        key: 'Sine Wave', //key  - the name of the series.
        color: '#ff7f0e'  //color - optional: choose your own line color.
      },
      {
        values: cos,
        key: 'Cosine Wave',
        color: '#2ca02c'
      },
      {
        values: sin2,
        key: 'Another sine wave',
        color: '#7777ff',
        area: true      //area - set to true if you want this line to turn into a filled area chart.
      }
    ];
  }
});

// Directive to generate a line graph
analyticsApp.directive('lineGraph', function($parse, $window){
});

// Directive to generate a pie chart
analyticsApp.directive('pieChart', function(){
});
