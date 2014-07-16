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
    screens output, this theme (overview) specifics (zonehtml, post fadein/out)

*************************************************************/

// Returns the HTML for a zone area
// TODO: This should really be templated out.
function zone_html(id, top, left, bottom, right) {
    return ('<div id="_zone_' + id + '" class="zone" style="display:block;width=100%;height:5em"></div>');
}

/***************************************************************************/

function post_fadeout(post, fadetime, andthen) {

    if (!andthen) { andthen = function() {}; }

    /*$(post._el).fadeOut(fadetime, andthen);*/
    $(post.el).css({'border': '2px solid black', 'opacity':'80%'});
    andthen()
}

function post_fadein(post, fadetime, andthen) {

    if (!andthen) { andthen = function() {}; }

    $(post.el).fadeIn(fadetime, andthen);
    $(post.el).css({'border':'2px solid red', 'opacity':'100%'});
    if (! post.display_time ) {
        post.display_time = 1000;
        console.log('...');
    }
    console.log(post.display_time);
    andthen();
}

function post_display() {}
function post_hide() {}
function post_render(post_data, zone) {
    "use strict";
    return post_types[post_data.type].render(zone.el, post_data).css('opacity',1)[0];
}
