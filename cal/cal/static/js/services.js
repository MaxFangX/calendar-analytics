var analyticsApp = window.angular.module('analyticsApp.services', []);

var analyticsApp.service("TagService", function TagService() {
  this.tags = {};

  this.getAllTags = function() {
    return $http({method: 'GET', url: '/v1/tags/.json' });
  }
}
