analyticsApp.component('calendar', {
  templateUrl: '/static/js/components/calendar/calendar.html',
  controller:  ['$scope', '$http', '$q', 'uiCalendarConfig', 'CalendarFilterService', 'CalendarSelect',  CalendarCtrl],
});

function CalendarCtrl($scope, $http, $q, uiCalendarConfig, CalendarFilterService, CalendarSelect) {
   this.calendars = CalendarSelect.calendars;
   var _this = this;

   this.events = function(start, end, timezone, callback) {
     var query_timezone = '';
     if (!timezone) {
       query_timezone = 'UTC';
     } else if (timezone === 'local') {
       query_timezone = moment.tz.guess();
     } else {
       query_timezone = timezone;
     }

     $http({
       method: 'GET',
       url: "/v1/gcalendars.json",
       cache: true,
     }).then(function gcalSuccess(response) {

       CalendarSelect.initialize(response);

       // Trigger first CalendarFilter now that CalendarSelect.calendars has been set
       CalendarFilterService.setFilter(start, end,
         CalendarSelect.getEnabledCalendarIds());
       var calendarIds = response.data.results.map(function(cal) {
         return cal.calendar_id;
       }).sort();

       $http({
         method: 'GET',
         url: "/v1/gevents.json",
         cache: true,
         params: {
           calendarIds: JSON.stringify(calendarIds),
           start: start.toISOString(),
           end: end.toISOString(),
           timezone: query_timezone,
           edge: 'truncated'
         },
       }).then(function eventSuccess(response) {
         var events = [];
         for (i = 0; i < response.data.results.length; i++) {
           var gevent = response.data.results[i];
           if (CalendarSelect.calendars[gevent.calendar.calendar_id].enabled) {
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
           }
         }

         callback(events);

       }, function eventError(response) {
         console.log("Ajax call to gevents failed:");
         console.log(response);
       });


     }, function gcalError(response) {
       console.log("Ajax call to gcalendars failed: " + response);
     });
   };

   $scope.eventRender = function(event, element, view) {
     /* jshint unused:vars */
     var location = '';
     if (event.location !== '') {
       location = '<i>' + event.location + '</i><br>';
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
     return element;
   };

   this.loading = function(isLoading, view){
      if (isLoading) {
        $('#calendar-preloader').show();
        $('.calendar').hide();
      } else {
        $('#calendar-preloader').hide();
        $('.calendar').show();
      }
    }.bind(this);

   this.viewRender = function(view, element) {

     /* jshint unused:vars */
     // The first time viewRender is called, the GCalendars haven't been
     // populated yet.
     if(CalendarSelect.calendars.length !== 0) {
       CalendarFilterService.setFilter(view.start, view.end,
                                       CalendarSelect.getEnabledCalendarIds());
     }
   }.bind(this);

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
       eventRender: $scope.eventRender,
       viewRender: this.viewRender,
       loading: this.loading
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
     }).then(
       function toggledSuccess(data) {
         /* jshint unused:vars */
       },
       function toggledFail(data) {
         /* jshint unused:vars */
         console.log("Could not save preferences for calendar " + calendarPrimaryKey);
       }
     ).then(function() {
       CalendarFilterService.setFilter(null,
                                       null,
                                       CalendarSelect.getEnabledCalendarIds());
     });
   };

   this.eventSources = [this.events];
}
