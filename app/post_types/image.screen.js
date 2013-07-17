{
    render: function(zone, data) {
        console.log('making img');
        console.log(data.content.file_url);
        return ($('<div class="post post_image" style="background-image: url('
                 + data.content.file_url
                 + ');background-repeat:no-repeat;background-size:contain;background-position: center center;"></div>').css('display','none')
                .prependTo(zone));
    }
}
