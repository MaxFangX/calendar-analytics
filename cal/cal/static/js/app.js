var analyticsApp = angular.module('analyticsApp', ['ui.calendar']);

analyticsApp.controller('LoggedInCtrl', function LoggedInController($scope) {

  $scope.testString = "hello angular 1.5!";

});

analyticsApp.controller('CalendarCtrl', function UiCalendarCtrl($scope, $compile, uiCalendarConfig) {

    $scope.events = function(start, end, timezone, callback) {
      var query_timezone = '';
      if (!timezone) {
        query_timezone = 'UTC';
      } else if (timezone === 'local') {
        query_timezone = moment.tz.guess();
      } else {
        query_timezone = timezone;
      }
      allEvents = [];
      $.ajax({
        url: "/v1/gcalendars.json",
        dataType: 'json',
        data: {},
      }).done(function(data) {
        $.when.apply(this, data.results.map(function(cal) {
          return $.ajax({
            url: "/v1/gevents.json",
            dataType: 'json',
            data: {
              calendarId: cal.calendar_id,
              start: start.toISOString(),
              end: end.toISOString(),
              timezone: query_timezone,
              edge: 'truncated'
            },
            success: function(data) {
              var events = [];
              $.each(data.results, function(index, gevent) {
                events.push({
                  title: gevent.name,
                  start: gevent.start,
                  end: gevent.end,
                  backgroundColor: gevent.color.background,
                  textColor: gevent.color.foreground,
                  borderColor: gevent.color.foreground,
                })
              });
              allEvents = allEvents.concat(events);
            }
          });
        })).then(function() {
          callback(allEvents);
        });
      });
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

    $scope.eventSources = [$scope.events];
})
