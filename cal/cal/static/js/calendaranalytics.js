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
