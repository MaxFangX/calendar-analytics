var analyticsApp = angular.module('analyticsApp', ['nvd3']);

// Test controller for logging in
analyticsApp.controller('LoggedInController', function LoggedInController($scope) {
});

// Controller to generate graph data from chart directive, cumulative tags
analyticsApp.controller('TagsController', function($scope, $http){
  var url = '/v1/tags';
});

// Example line graph in categories, line graph per week
analyticsApp.controller('CategoriesController', function($scope, $http){
  var url = '/v1/colorcategories';

  $http({ method: 'GET', url: url }).
    success(function (data) {
      // set the data
      $scope.data = [];
      for (var i = 0; i < data.results.length; i++) {
        var category = data.results[i];
        $scope.data.push( {
          category: category.label,
          hours: category.hours
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
      text: 'Total Hours Spent from Categories'
    },
  };
});

// Directive to generate a line graph
analyticsApp.directive('lineGraph', function($parse, $window){
});

// Directive to generate a pie chart
analyticsApp.directive('pieChart', function(){
});
