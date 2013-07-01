$('#post_type').change(function (e) {
    $('#contentblock').load(window.POST_TYPE_URL($(this).val()));
});
