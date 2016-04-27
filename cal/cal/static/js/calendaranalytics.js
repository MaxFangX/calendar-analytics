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
                $.each(data.results, function(index, tag) {
                    label = tag.label;
                    keywords = tag.keywords;
                    $('<li>' + label + ': ### hours </li>').addClass('list-group-item').appendTo('.cal-tag-list .list-group')
                });
            }
        });
    }
});
