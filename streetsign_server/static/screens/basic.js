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

if (!window.hasOwnProperty('requestAnimationFrame')){
    try {
        window.requestAnimationFrame = mozRequestAnimationFrame;
    } catch (ignore) {
        window.requestAnimationFrame = webkitRequestAnimationFrame;
    }
}

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
        //$(post.zone.el).css('opacity', 0);
        post.zone.el.style.opacity = 0;
        post.el.style.transition = "";
        post.el.style.webkitTransition = "";
        post.el.style.mozTransition = "";


        setTimeout( function () {
            post.el.style.opacity = 0;
            post.zone.el.style.opacity = 1.0;
            andthen()
        }, post.zone.fadetime);

    } else {
        post.el.className = post.el.className.replace(' faded_in','');
        setTimeout( function () {
            post.el.style.display = 'none';
            andthen();
        }, post.zone.fadetime);

    }
}

function post_fadein(post, fadetime, andthen) {
    "use strict";
    var distance;
    var dotick;
    var current;
    var current_set;

    if (!andthen) { andthen = _mt; }

    post.el.style.display = "block";

    if (post.zone.type == 'scroll') {


        distance = post.el.offsetWidth + post.zone.el.offsetWidth + 20;

        //el.style.display = "block";
        post.el.style.marginLeft = (post.zone.el.offsetWidth + 10) + "px";
        setTimeout( function () { 

            post.el.style.opacity = "1.0";
            post.el.style.transition = "margin " + (distance/70) + "s linear";
            post.el.style.webkitTransition = "margin " + (distance/70) + "s linear";
            post.el.style.mozTransition = "margin " + (distance/70) + "s linear";
            post.el.style.marginLeft = (-10 - post.el.offsetWidth) + "px";

            andthen();
        }, 10);

        post.display_time = (distance + 100) * 14;


    } else {
        fadetime = 1 * fadetime;
        if ((fadetime === undefined)||(isNaN(fadetime))) { fadetime = 0; }
        post.el.className += ' faded_in';
        setTimeout(andthen, fadetime);
    }
}

