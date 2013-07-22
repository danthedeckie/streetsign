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
function zone_html(id, top, left, bottom, right) {
    return ('<div id="_zone_'+id+'" class="zone" style="display:inline; width: 40%;min-height: 40%;float:left"></div>');
}

/***************************************************************************/

function post_fadeout(post, fadetime, andthen=function(){}) {
    /*$(post._el).fadeOut(fadetime, andthen);*/
    $(post._el).css('border', '2px solid red');
    andthen();
}

function post_fadein(post, fadetime, andthen=function(){}) {
    $(post._el).fadeIn(fadetime, andthen);
    
    $(post._el).css('border','2px solid black');
    andthen();
}

