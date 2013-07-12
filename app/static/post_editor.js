$('.post_type_button').click(function (e) {
    // POST_TYPE_URL dynamically from page.
    $('#postcontentblock').load(
        window.POST_TYPE_URL($(this).data('posttype'))
        );


    // TODO: put these in CSS classes...
    $('.post_type_button').parent().css('background','#ccc');
    $(this).parent().css('background','#aaa');

});
