/* Messy - this gets the post types as json, and turns it into
           options for use in a select box. */

/*
$.getJSON('/js/post_types.json', function(data) {
    var items = [];

    $.each(data["types"], function (item) {
        var i = data["types"][item];
        items.push('<option value="' + i.id + '">' + i.name + '</option>');
    });
    $(items.join('')).appendTo('.post_type_selector');
}); */

$('select.chosen').chosen({'width':'100%'});
