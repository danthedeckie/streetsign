{
    render: function(zone, data) {

        var newhtml = $('<div class="post post_text"><div class="post_inner">'
                + magic_vars( data.content.content)
                + '</div></div>')
                .prependTo(zone);

        console.log('making new text-post');

        reduce_font_size_to_fit(newhtml.children('.post_inner'), $(zone));

        return newhtml;
    }
}
