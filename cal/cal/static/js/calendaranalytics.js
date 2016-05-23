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
                    return a.label.localeCompare(b.label)
                });
                $.each(data.results, function(index, tag) {
                    $('<li>' + tag.label + ': ' + tag.hours + ' hours </li>').addClass('list-group-item').appendTo('.cal-tag-list .list-group');
                });
            }
        });
    }
});
