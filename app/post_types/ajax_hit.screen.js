{
    render: function(zone, data) {
        $.post(data.content.render_url);
        // honestly a bit pointless...
        return($('<div class="post post_video">...</div>')
               .prependTo(zone));
    },
    display: function(data) {
        console.log('Trying to start local stream-player')
        $.post(data.content.display_url);
    },
    hide: function(data) {
        console.log('Trying to stop local stream-player')
        $.post(data.content.hide_url);
    }
}

