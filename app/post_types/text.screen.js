{
    render: function(zone, data) {
        console.log('making text');
        return ($('<div class="post post_text"><pre>' 
                  + magic_vars(data.content.content)
                  + '</pre></div>')
                .prependTo(zone));
    }
}
