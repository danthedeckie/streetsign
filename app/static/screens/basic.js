/************************************************************

    Concertino Digital Signage Project
     (C) Copyright 2013 Daniel Fairhead

    Concertino is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Concertino is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Concertino.  If not, see <http://www.gnu.org/licenses/>.

    ---------------------------------
    screens output, this theme (basic) specifics (zonehtml, post fadein/out)

*************************************************************/

// Returns the HTML for a zone area
// TODO: This should really be templated out.
function zone_html(id, top, left, bottom, right, css, type) {
    console.log('TYPE: zone_' + type + '...');
    return ('<div id="_zone_'+id+'" class="zone zone_'+type+'" style="'
            +'left:' + left
            +';right:' + right
            +';bottom:' + bottom
            +';top:' + top + '"></div>');
}

/***************************************************************************/

function post_fadeout(post, fadetime, andthen) {
    if (!andthen) { andthen = function() {}; }

    if (('type' in post.zone) && (post.zone.type == 'scroll')) {
        // do scroll stuff.
        andthen();
    } else {
        $(post._el).fadeOut(fadetime, andthen);
    }
}

function post_fadein(post, fadetime, andthen) {
    if (!andthen) { andthen = function() {}; }

    if (('type' in post.zone) && (post.zone.type == 'scroll')) {
        var distance = $(post._el).width() + $(post.zone.el).width() + 20;
        $(post._el).fadeIn(0, andthen);
        $(post._el).css('left', $(post.zone.el).width() + 10);
        $(post._el).animate({'left': 0 - ($(post._el).width() + 10)}, distance * 10, 'linear'  );


        // do scroll stuff.
    } else {
        $(post._el).fadeIn(fadetime, andthen);
    }
}

