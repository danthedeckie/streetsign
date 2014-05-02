{
    render: function(zone, data) {
        'use strict';
        var newhtml = '';                   // html to append in to the zone.

        console.log('embedding new external webpage');

        newhtml = ('<iframe scrolling="no" width="'+ $(zone).width()+'" height="' + $(zone).height() + '" frameborder="no" src="'
                  + data.content.url
                  + '">...</iframe>');

        if (('type' in data.zone ) && ( data.zone.type == 'scroll')) {
            newhtml = $('<div class="post post_html post_scrolling"><div class="post_inner">'
                        + newhtml
                        + '</div></div>').prependTo(zone);
        } else {
            newhtml = $('<div class="post post_html"><div class="post_inner">'
                    + newhtml
                    + '</div></div>')
                    .prependTo(zone);
        }

        // Return the HTML object, hiding it along the way.

        return newhtml;
    }
}
