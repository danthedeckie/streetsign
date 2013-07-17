{
    render: function(zone, data) {
        console.log('making new text-post');
        var height = 0;
        var zone_height = $(zone).height()
        var newhtml = $('<div class="post post_text"><div class="post_inner">'
                + magic_vars( data.content.content
                              .replace(/&/g,'&amp;')
                              .replace(/</g,'&lt;')
                              .replace(/>/g,'&gt;'))
                + '</div></div>')
                .prependTo(zone);

        height = newhtml.children('.post_inner').height();
        if ( height > zone_height ) {
            for (var i=100; i>10;i-=3){

                height = newhtml.children('.post_inner').height();
                //console.log ( zone_height + ':' + height);
                if (height <= zone_height) {
                    console.log ('setting size to ' + i + '%');
                    break;
                }
                newhtml.children('.post_inner').css('font-size', i + '%');
            }
        }
        return newhtml.css('display','none');
    }
}
