/*jslint browser:true, regexp: true, debug: true */
/*global $, jLater, confirm, alert */
////////////////////////////////////////////////
// Flashed notices:
$('#flashed_notices').children('li').click(function(){
    $(this).fadeOut();
});
setTimeout( function () { $('#flashed_notices > li').fadeOut('slow'); }, 15000);

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

    var dom_item = $(this).parents('*[data-item]');

    evt.preventDefault();

    if (confirm('Really delete?')) {
        dom_item.slideUp();
        $.ajax({
            url: $(dom_item).data('item'),
            type: 'DELETE',
            success: function(resp) {
                dom_item.slideUp('fast', dom_item.remove);
                flash('deleted');
                },
            error: function(resp) {
                dom_item.slideDown();
                flash('could not delete!');
                }
            });
    }

});

$('.popup_ask').click(function(evt) {
  /* fills in a form value.  If attached to a submit button,
     will submit the form as well. */

  var input = $(this.form).find("input[name=" + $(this).data("inputname") + "]"),
      value = prompt($(this).data("prompt"), $(this).data("autofill"));

  if (value) {
      input.val(value);
  } else {
      evt.preventDefault();
  }
  //$.post( this.form.getAttribute('action'), $(this.form).serialize(), function(data) {
});

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

$('#run_housekeeping').click(function() {
    $.post(window.HOUSEKEEPING_URL, {}, function(data) {
        alert("Housekeeping Done! \n" +
              data.archived + " posts archived. \n" +
              data.deleted + " posts deleted");
        }, 'json');

});


// and run any js which was inserted by a template, which needs jQuery.

while (jLater.length) {
    jLater.pop()($);
}

////////////////////////////////

$(document).on('click', '.item_ajax_toggle', function() {
    var toggle_class = $(this).data('ajaxtoggle'),
        item = $(this).parents('.item').first().toggleClass(toggle_class),
        data = {};

    data[$(this).data('name')] = $(this).data('value');

    $.ajax($(this).parents('[data-uri]').data('uri'),
           { type: $(this).data('ajaxtype'),
             data: data,
             error: function() {
                item.toggleClass(toggle_class);
                alert('failed to delete!');
                }});
});

$(function() {
    $('.autopost').change(function() {
        $.post( this.form.getAttribute('action'), $(this.form).serialize(), function(data) {
            if (data.message) {
                flash(data.message);
            } else {
                flash(data);
            }
        });
    });
});


