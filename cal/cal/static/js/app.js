var analyticsApp = angular.module('analyticsApp', ['nvd3', 'ui.calendar']);

analyticsApp.controller('LoggedInCtrl', function LoggedInController($scope) {
});

analyticsApp.controller('TagsCtrl', function($scope, $http){
  var tagUrl = '/v1/tags';
  $scope.tags = [];
  $scope.orderByField = 'label';
  $scope.reverseSort = false;

  // Generate graph data
  $http({method: 'GET', url: tagUrl + '.json' }).
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

  this.create = function(tag) {
    $http({
      method: 'POST',
      url: tagUrl + '.json',
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
        editing: false
      });
    });
  };

  this.startEdit = function(tagId) {
    var tag = $scope.tags.find(function(tag, index, array) { return tag.id == tagId; });
    tag.newLabel = tag.label;
    tag.newKeywords = tag.keywords;
    tag.editing = true;
  };

  this.submit = function(tagId) {
    var tag = $scope.tags.find(function(tag, index, array) { return tag.id == tagId; });
    tag.editing = false;

    $http({
      method: 'POST',
      url: tagUrl + '/' + tagId,
      data: $.param({
        label: tag.newLabel,
        keywords: tag.newKeywords,
        csrfmiddlewaretoken: getCookie('csrftoken'),
        _method: 'PATCH'
      }),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    }).
    success(function addToList(data) {
      tag.label = data.label;
      tag.keywords = data.keywords;
      tag.hours = data.hours;
    });
  };

  this.cancelEdit = function(tagId) {
    var tag = $scope.tags.find(function(tag, index, array) { return tag.id == tagId; });
    tag.editing = false;
  };

  this.delete = function(tagId) {
    $http({
      method: 'POST',
      url: tagUrl + '/' + tagId,
      data: $.param({
        csrfmiddlewaretoken: getCookie('csrftoken'),
        _method: 'DELETE'
      }),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    }).
    success(function removeFromList(data) {
      $scope.tags = $scope.tags.filter(function(tag) {
        return tag.id !== tagId;
      });
    });
  };
});

analyticsApp.component('tags', {
    templateUrl: 'static/templates/tags.html',
    controller: 'TagsCtrl',
    controllerAs: '$ctrl',
    bindings: {}
});

analyticsApp.controller('CategoriesCtrl', function($scope, $http){
  var url = '/v1/colorcategories.json';
  $scope.orderByField = 'label';
  $scope.reverseSort = false;

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
          $scope.calendars[gcal.calendar_id].enabled = gcal.enabled_by_default;
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
              allDay: gevent.all_day_event,
              backgroundColor: gevent.color.background,
              textColor: gevent.color.foreground,
              borderColor: gevent.color.foreground,
              description: gevent.description,
              location: gevent.location,
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
  $scope.eventRender = function(event, element, view) {
    var location = ''
    if (event.location !== '') {
      location = '<i>' + event.location + '</i><br>'
    }
    element.qtip({
      content: '<b>' + event.title + '</b><br>' + location + event.description,
      show: 'click',
      hide: 'unfocus',
      position: {
        target: 'mouse',
        viewport: $(window),
        adjust: {
          mouse: false,
          method: 'flip shift'
        }
      },
      style: {
        classes: 'cal-section-info'
      },
    });
    return element
  }
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
      eventClick: $scope.alertOnEventClick,
      eventRender: $scope.eventRender,
    }
  };

  this.refresh = function(calendarName) {
    if(uiCalendarConfig.calendars[calendarName] !== undefined){
      uiCalendarConfig.calendars[calendarName].fullCalendar('refetchEvents');
    }
  };

  this.toggleEnabled = function(calendarPrimaryKey) {
    $http({
      method: 'GET',
      url: "/v1/gcalendars/" + calendarPrimaryKey + "/toggle-enabled/"
    }).then(function toggledSuccess(data) {}, function toggledFail(data) {
      console.log("Could not save preferences for calendar " + calendarPrimaryKey);
    });
  };
  
  this.eventSources = [this.events];
});
