var analyticsApp = angular.module('analyticsApp', ['nvd3']);

// Test controller for logging in
analyticsApp.controller('LoggedInController', function LoggedInController($scope) {

  $scope.testString = "hello angular 1.5!";

});

// Controller to generate graph data from chart directive
analyticsApp.controller('TagsController', ['$scope', function($scope){
  $scope.data = [
    { key: "One", y: 5 },
    { key: "Two", y: 2 },
    { key: "Three", y: 9 },
    { key: "Four", y: 7 },
    { key: "Five", y: 4 },
    { key: "Six", y: 3 }
  ];
  $scope.options = {
    chart: {
      type: 'pieChart',
      height: 500,
      x: function(d){return d.key;},
      y: function(d){return d.y;},
      showLabels: true,
      duration: 500,
      labelThreshold: 0.01,
      labelSunbeamLayout: true,
      legend: {
        margin: {
          top: 5,
          right: 35,
          bottom: 5,
          left: 0
        }
      }
    }
  };
  // $scope.options = pieChart.options;


}]);

// Directive to generate a line graph
analyticsApp.directive('lineGraph', function($parse, $window){
});

// Directive to generate a pie chart
analyticsApp.directive('pieChart', function(){
});
