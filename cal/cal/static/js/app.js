var analyticsApp = angular.module('analyticsApp', ['ui.calendar']);

analyticsApp.controller('LoggedInCtrl', function LoggedInController($scope) {

  $scope.testString = "hello angular 1.5!";

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
