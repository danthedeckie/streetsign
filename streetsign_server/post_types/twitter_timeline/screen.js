{
    _template: function(query, width, height) {
    return '<a class="twitter-timeline" data-dnt="true" href="https://twitter.com/' + query + '"'
         + ' width="' + width + '" height="' + height + '"'
         + ' data-screen-name="' + query + '"'
         + ' data-chrome="nofooter transparent noscrollbar noheader"'
         + ' data-widget-id="494072388510687232">Loading tweets from ' + query + '<' + '/a>'
         + '<script src="//platform.twitter.com/widgets.js"><' + '/script>';
         /* 
         + '<script>
         + '<scr'+ 'ipt>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?\'http\':\'https\';if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+"://platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");<' + '/script>' */
    },

    render: function(zone, data) {
        'use strict';
        var newhtml = '';                   // html to append in to the zone.

        console.log('embedding new twitter widget');

        newhtml = this._template(data.content.query, $(zone).width(), $(zone).height());

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
