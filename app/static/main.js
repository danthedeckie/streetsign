////////////////////////////////////////////////
// Flashed notices:
$('#flashed_notices > li').click(function(){
    $(this).fadeOut();
});
$('#flashed_notices > li').delay(15000).fadeOut('slow');
//

////////////////////////////////////////////////
// Nice 'chosen' select boxes:

$('select.chosen').chosen({'width':'100%'});

////////////////////////////////////////////////
// User login/details popup box thingy:

$('#user_login_button').click( function ()
{
    $('#login_box').fadeToggle();
}
);

/* Confirmation buttons: */

$('.confirm_delete').click(function () {
    return (confirm('Really delete?'));
});
