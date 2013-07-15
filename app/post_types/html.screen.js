{
    render: function(zone, data) {
        console.log('making html');
        return $('<div class="post post_html">'
                + magic_vars(data.content.content)
                + '</div>')
                .prependTo(zone);
    }
}
