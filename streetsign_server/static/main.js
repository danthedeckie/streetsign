////////////////////////////////////////////////
// Flashed notices:
$('#flashed_notices li').click(function(){
    $(this).fadeOut();
});

$('#flashed_notices > li').delay(15000).fadeOut('slow');

function flash(text) {
    $('#flashed_notices').append($('<li>' + text + ' </li>').click(function(){$(this).fadeOut();}));
}

////////////////////////////////////////////////
// Nice 'chosen' select boxes:

$('select.chosen').chosen({'width':'100%'});

/* Confirmation buttons: */

$('.confirm_delete').click(function () {
    return (confirm('Really delete?'));
});

$('a.confirm_ajax_delete').click(function(evt) {
    /* smart ajax class, sends DELETE HTTP request to specified URL,
       and looks for parent specified in data-item, which it hides upon
       request sent, and deletes upon success, or restores on failure. */

    var dom_item = $(this).parents($(this).data('item'));

    evt.preventDefault();

    if (confirm('Really delete?')) {
        dom_item.slideUp();
        $.ajax({
            url: $(this).attr('href'),
            type: 'DELETE',
            success: function(resp) {
                dom_item.remove();
                flash('deleted');
                },
            error: function(resp) {
                dom_item.slideDown();
                flash('could not delete!');
                }
            });
    }

});

// And why not, lets also check if new data needs to be got (which
// will then happen every time any back end page is checked.)
$.post('/external_data_sources/');

// focus on username input box when 'login' clicked.
$('#user_login_button').click(function(){
    setTimeout( function() {
        $('input[name="username"]').focus();
    }, 500);
});

// hide expired posts, unless cookie says don't.

if ($.cookie('show_past_posts') === "true") {
    $('.time_past').show();
    $('#show_past_posts').addClass('active');
} else {
    $('.time_past').hide();
}

$('#show_past_posts').click(function() {
    $('.time_past').toggle();
    $(this).toggleClass('active');
    $.cookie('show_past_posts', $.cookie('show_past_posts') === "true" ? "false" : "true",
             {"path": "/"});
});

// and run any js which was inserted by a template, which needs jQuery.

while (jLater.length) {
    jLater.pop()($);
}


