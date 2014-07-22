{
    render: function(zone, data) {
        'use strict';
        var newhtml = '';                   // html to append in to the zone.

        console.log('making new html');

        if (('type' in data.zone ) && ( data.zone.type == 'scroll')) {
            newhtml = $('<div class="post post_html post_scrolling"><div class="post_inner">'
                           + magic_vars(data.content.content).replace('<br/>',' ')
                           + '</div></div>').prependTo(zone);
        } else {

            newhtml = $('<div class="post post_html"><div class="post_inner">'
                    + magic_vars(data.content.content)
                    + '</div></div>')
                    .prependTo(zone);
        }

        // Reduce font size until it fits nicely:

        reduce_font_size_to_fit(newhtml.children('.post_inner'), $(zone));

        // Set font color:
        if (data.content.owntextcolor) {
            try{newhtml.css('color',data.content.color);}catch(e){};
        }
        // Return the HTML object, hiding it along the way.

        return newhtml;
    }
}
