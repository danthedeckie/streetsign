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

/* Confirmation buttons: */

$('.confirm_delete').click(function () {
    return (confirm('Really delete?'));
});
