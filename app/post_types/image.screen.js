{
    render: function(zone, data) {
        console.log('making img');
        console.log(data.content.file_url);
        return ($('<div class="post post_image"><img src="'
                 + data.content.file_url
                 + '" style="width:100%;height:auto;" /></div>')
                .prependTo(zone));
    }
}
