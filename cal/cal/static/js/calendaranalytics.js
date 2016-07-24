// Helper function to grab cookies, mostly for csrf
// Use like this:
// var csrftoken = getCookie('csrftoken');
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(document).ready(function() {
    taglist = $('.cal-tag-list');
    if (taglist.length !== 0) {
        $.ajax({
            url: "/v1/tags.json",
            dataType: 'json',
            data: {
            },
            success: function(data) {
                tags = [];
                data.results.sort(function(a, b) {
                    return a.label.localeCompare(b.label);
                });
                $.each(data.results, function(index, tag) {
                    $('<li>' + tag.label + ': ' + tag.hours + ' hours </li>').addClass('list-group-item').appendTo('.cal-tag-list .list-group');
                });
            }
        });
    }
});

$(document).ready(function() {
    var calendarIds = null;
    $('#calendar').fullCalendar({
        defaultView: 'agendaWeek',
        events: function(start, end, timezone, callback) {
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
                            // {% if request.user.is_staff %}
                            // title: gevent.id + " " + gevent.name,
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

        },
        timezone: 'local',
    })
});
