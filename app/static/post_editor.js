$('.post_type_button').click(function (e) {
    // POST_TYPE_URL dynamically from page.
    $('#contentblock').load(
        window.POST_TYPE_URL($(this).data('posttype'))
        );
    $('.post_type_button').parent().css('background','#ccc');
    $(this).parent().css('background','#aaa');

});
