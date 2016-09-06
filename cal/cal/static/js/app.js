var analyticsApp = angular.module('analyticsApp', ['nvd3', 'ui.calendar']);

analyticsApp.controller('LoggedInCtrl', function LoggedInController($scope) {
});

// Controller to generate graph data from chart directive, cumulative tags
analyticsApp.controller('TagsCtrl', function($scope, $http){
  var url = '/v1/tags.json';
  $scope.url = url;
  $scope.tags = [];

  $http({ method: 'GET', url: url }).
    success(function successCallback(data) {

      for (var i = 0; i < data.results.length; i++) {
        var tag = data.results[i];
        $scope.tags.push({
          label: tag.label,
          keywords: tag.keywords,
          hours: tag.hours
        });
      }

    });

});

// Example line graph in categories, line graph per week
analyticsApp.controller('CategoriesCtrl', function($scope, $http){
  var url = '/v1/colorcategories.json';

  $http({ method: 'GET', url: url }).
    success(function (data) {
      // set the data
      $scope.categories = [];
      for (var i = 0; i < data.results.length; i++) {
        var category = data.results[i];
        $scope.categories.push({
          label: category.label,
          hours: category.hours
        });
      }
    });

  $scope.options = {
    chart: {
      type: 'pieChart',
      height: 500,
      x: function(d){return d.label;},
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

analyticsApp.controller('CalendarCtrl', function UiCalendarCtrl($scope, $http, $q, uiCalendarConfig) {

    $scope.calendars = {}

    this.events = function(start, end, timezone, callback) {
        var query_timezone = '';
        if (!timezone) {
            query_timezone = 'UTC';
        } else if (timezone === 'local') {
            query_timezone = moment.tz.guess();
        } else {
            query_timezone = timezone;
        }
        allEvents = [];

        $http({
            method: 'GET',
            url: "/v1/gcalendars.json",
            cache: true,
        }).then(function gcalSuccess(response) {

            var collectedEvents = [];
            var eventPromises = response.data.results.map(function(gcal) {

              // Initialize cached calendars
              if ($scope.calendars[gcal.calendar_id] === undefined) {
                  $scope.calendars[gcal.calendar_id] = gcal;
                  $scope.calendars[gcal.calendar_id].enabled = true;
              }

              return $http({
                  method: 'GET',
                  url: "/v1/gevents.json",
                  cache: true,
                  params: {
                      calendarId: gcal.calendar_id,
                      start: start.toISOString(),
                      end: end.toISOString(),
                      timezone: query_timezone,
                      edge: 'truncated'
                  },
              }).then(function eventSuccess(response) {
                  var events = [];
                  $.each(response.data.results, function(index, gevent) {
                      events.push({
                          title: gevent.name,
                          start: gevent.start,
                          end: gevent.end,
                          backgroundColor: gevent.color.background,
                          textColor: gevent.color.foreground,
                          borderColor: gevent.color.foreground,
                      })
                  });

                  if ($scope.calendars[gcal.calendar_id].enabled) {
                      collectedEvents = collectedEvents.concat(events);
                  }
              }, function eventError(response) {
                  console.log("Ajax call to gevents failed: " + response);
              });
            });

            $q.all(eventPromises).then(function() {
                callback(collectedEvents);
            });

        }, function gcalError(response) {
            console.log("Ajax call to gcalendars failed: " + response);
        })

    };

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
      }
    };

    this.refresh = function(calendarName) {
      if(uiCalendarConfig.calendars[calendarName] !== undefined){
        uiCalendarConfig.calendars[calendarName].fullCalendar('refetchEvents');
      }
    };

    this.eventSources = [this.events];
});
