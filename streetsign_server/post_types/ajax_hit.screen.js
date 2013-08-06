{
    render: function(zone, data) {
        $.post(data.content.render_url);
        // honestly a bit pointless...
        return($('<div class="post post_video">...</div>')
               .prependTo(zone));
    },
    display: function(data) {
        var url = (data.content.display_url.match(/.*:\/\/.*/) != -1 ? 'http://' : '') + data.content.display_url;
        console.log('Trying to start local stream-player: ' + url);
        $('#zones').fadeOut();
        $.post(url);
        
    },
    hide: function(data) {
        var url = (data.content.display_url.match(/.*:\/\/.*/) != -1 ? 'http://' : '') + data.content.hide_url;
        console.log('Trying to stop local stream-player: ' + url)
        $('#zones').fadeIn();
        $.post(url);
    }
}

