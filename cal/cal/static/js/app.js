/*jslint devel: true, browser: true, jquery: true */

var analyticsApp = window.angular.module('analyticsApp', [
  'analyticsApp.services',
  'nvd3',
  'ui.calendar',
  'ui.router'
]);


analyticsApp.config(['$stateProvider', function ($stateProvider) {

  $stateProvider.state('home', {
    url: '',
    component: 'calendar'
  });

  // TODO: refactor $stateParams => $transition$.parms()
  $stateProvider.state('tag-details', {
    url: '/tag/{tagId}',
    params: { /* defining optional params that don't appear in url */
      label: { type: 'string' },
      keywords: { type: 'string' }
    },
    resolve: {
      // TODO: fetch label if not in state params
      label: function($stateParams) { return $stateParams.label; },
      keywords: function ($stateParams) { return $stateParams.keywords; },
      tagId: function($stateParams) { return $stateParams.tagId; }
    },
    component: 'tagDetails'
  });

  $stateProvider.state('category-details', {
    url: '/category/{categoryId}',
    params: { /* defining optional params that don't appear in url */
      displayName: { type: 'string' },
      categoryHours: { type: 'string' }
    },
    resolve: { 
      displayName: function($stateParams) { return $stateParams.displayName; },
      categoryId: function ($stateParams) { return $stateParams.categoryId; },
      categoryHours: function ($stateParams) { return $stateParams.categoryHours; }
    },
    component: 'categoryDetails'
  });

}]);

// Debugging
analyticsApp.run(function($rootScope) {
    $rootScope.$on("$stateChangeError", console.log.bind(console));
});

