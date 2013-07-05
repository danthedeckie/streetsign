$('#post_type').change(function (e) {
    // POST_TYPE_URL dynamically from page.
    $('#contentblock').load(
        window.POST_TYPE_URL($(this).val())
        );

});
