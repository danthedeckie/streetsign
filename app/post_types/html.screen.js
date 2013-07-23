{
    render: function(zone, data) {
        if (('type' in data.zone ) && ( data.zone.type == 'scroll')) {
            var newhtml = $('<div class="post post_html post_scrolling">'
                           + magic_vars(data.content.content).replace('<br/>',' ')
                           + '</div>').prependTo(zone);
            return newhtml.css('display','none');
        } else {

        console.log('making new html');
        var height = 0;
        var zone_height = $(zone).height()
        var newhtml = $('<div class="post post_html"><div class="post_inner">'
                + magic_vars(data.content.content)
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
        try{newhtml.css('color',data.content.color);}catch(e){};

        return newhtml.css('display','none');
    }
    }
}
