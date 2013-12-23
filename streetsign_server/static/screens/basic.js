/************************************************************

    StreetSign Digital Signage Project
     (C) Copyright 2013 Daniel Fairhead

    StreetSign is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    StreetSign is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with StreetSign.  If not, see <http://www.gnu.org/licenses/>.

    ---------------------------------
    screens output, this theme (basic) specifics (zonehtml, post fadein/out)

*************************************************************/

var _mt = function(){};

// Returns the HTML for a zone area
// TODO: This should really be templated out.
function zone_html(id, top, left, bottom, right, css, type) {
    "use strict";

    console.log('TYPE: zone_' + type + '...');
    return ('<div id="_zone_'+id+'" class="zone zone_'+type+'" style="'
            +'left:' + left
            +';right:' + right
            +';bottom:' + bottom
            +';top:' + top + '"></div>');
}

/***************************************************************************/

function post_fadeout(post, fadetime, andthen) {
    "use strict";

    if (!andthen) { andthen = _mt; }

    fadetime = 1 * fadetime;

    if ((fadetime === undefined)||(isNaN(fadetime))) { fadetime = 0; }

    if (post.zone.type == 'scroll') {
        // do scroll stuff.
        $(post.zone.el).css('opacity', 0);
        setTimeout( function () {
            $(post.el).css('opacity', 0);
            $(post.zone.el).css('opacity', 1.0);
            andthen()
        }, 1000);
    } else {
        //$(post.el).transition({'opacity':0}, fadetime, andthen);
        $(post.el).removeClass('faded_in');
        andthen();

    }
}

function post_fadein(post, fadetime, andthen) {
    "use strict";
    var distance;
    var el;
    var dotick;
    var current;
    var stopat;
    var current_set;

    if (!andthen) { andthen = _mt; }

    if (post.zone.type == 'scroll') {
        current = $(post.zone.el).width();

        post.zone.current_scroll_num = post.zone.current_scroll_num || 1;
        post.zone.current_scroll_num += 1;
        current_set = post.zone.current_scroll_num;

        distance = $(post.el).width() + current + 20;

        // This is odd..
        //$(post.el).fadeIn(0, andthen);
        //$(post.el).css('left', $(post.zone.el).width() + 10);
        
        $(post.el).css({'left': current + 10,
                        'opacity': 1.0});

        //$(post.el).animate({'left': 0 - ($(post.el).width() + 10)},
        //                      distance * 17,
        //                      'linear');
        el = $(post.el).get()[0];
        stopat = 0 - el.offsetWidth;

        dotick = function () {
        
            if ((current_set == post.zone.current_scroll_num)&&(current > stopat)) {
                current -= 1;
                el.style.left = current + 'px';
                requestAnimationFrame(dotick);
            } else {
                console.log('stopped');
            }
        }
        dotick();

        post.display_time = distance * 17;

        andthen();

    } else {
        fadetime = 1 * fadetime;
        if ((fadetime === undefined)||(isNaN(fadetime))) { fadetime = 0; }
        //$(post.el).transition({'opacity':1.0}, fadetime, andthen);
        $(post.el).addClass('faded_in');
        andthen();
    }
}

