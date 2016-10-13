var analyticsApp = angular.module('analyticsApp', ['nvd3', 'ui.calendar']);

analyticsApp.controller('LoggedInCtrl', function LoggedInController($scope) {
});

analyticsApp.controller('TagsCtrl', function($scope, $http){
  var url = '/v1/tags.json';
  var tagUrl = '/v1/tags/';

  $scope.url = url;
  $scope.tags = [];

  // Generate graph data
  $http({ method: 'GET', url: url }).
    success(function successCallback(data) {
      for (var i = 0; i < data.results.length; i++) {
        var tag = data.results[i];
        $scope.tags.push({
          id: tag.id,
          label: tag.label,
          keywords: tag.keywords,
          hours: tag.hours
        });
      }
    });

    this.addTag = function(tag) {
      $http({
        method: 'POST',
        url: url,
        data: $.param({
          label: tag.label,
          keywords: tag.keywords,
          csrfmiddlewaretoken: getCookie('csrftoken')
        }),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }).
        success(function addToList(data) {
          $scope.tags.push({
            id: data.id,
            label: data.label,
            keywords: data.keywords,
            hours: data.hours,
            original_label: data.label,
            original_keywords: data.keywords
          });
        });
    };

    this.editTag = function(tagId) {
      var tag = search(tagId, $scope.tags);

      $http({
        method: 'POST',
        url: tagUrl + tagId,
        data: $.param({
          label: tag.label,
          keywords: tag.keywords,
          csrfmiddlewaretoken: getCookie('csrftoken'),
          _method: 'PATCH'
        }),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }).
        success(function editToList(data) {
          tag.label = data.label;
          tag.keywords = data.keywords;
          tag.original_label = data.label;
          tag.original_keywords = data.keywords;
          tag.hours = data.hours;
        });
    };

    this.resetTag = function(tagId) {
      var tag = search(tagId, $scope.tags);

      $http({
        method: 'POST',
        url: tagUrl + tagId,
        data: $.param({
          label: tag.label,
          keywords: tag.keywords,
          csrfmiddlewaretoken: getCookie('csrftoken'),
          _method: 'PATCH'
        }),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }).
        success(function editToList(data) {
          tag.label = tag.original_label;
          tag.keywords = tag.original_keywords;
          tag.original_label = tag.original_label;
          tag.original_keywords = tag.keywords;
          tag.hours = tag.hours;
        });
    };

    this.deleteTag = function(tagId) {
      $http({
        method: 'POST',
        url: tagUrl + tagId,
        data: $.param({
          csrfmiddlewaretoken: getCookie('csrftoken'),
          _method: 'DELETE'
        }),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }).
        success(function removeTagFromList(data) {
          $scope.tags = $scope.tags.filter(function(tag) {
            return tag.id !== tagId;
          });
        });
    };

    function search(id, tags){
    for (var i=0; i < tags.length; i++) {
        if (tags[i].id === id) {
            return tags[i];
        }
      }
    }

});

analyticsApp.controller('CategoriesCtrl', function($scope, $http){
  var url = '/v1/colorcategories.json';

  // Generate graph data
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
      height: 400,
      x: function(d){return d.label;},
      y: function(d){return d.hours;},
      showLabels: true,
      growOnHover: true,
      duration: 500,
      labelThreshold: 0.01,
      labelSunbeamLayout: false,
      legend: {
        margin: {
          top: 5,
          right: 0,
          bottom: 0,
          left: 0
        }
      },
    },
  };
});

analyticsApp.controller('CalendarCtrl', function UiCalendarCtrl($scope, $http, $q, uiCalendarConfig) {

    $scope.calendars = {};

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
                      });
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

    this.refresh = function(calendarName) {
      if(uiCalendarConfig.calendars[calendarName] !== undefined){
        uiCalendarConfig.calendars[calendarName].fullCalendar('refetchEvents');
      }
    };

    this.eventSources = [this.events];
});
