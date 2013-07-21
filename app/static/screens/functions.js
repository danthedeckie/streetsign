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
    screens output, generic-ish functions.

*************************************************************/

function magic_vars(text) {
    'use strict';
    // replaces %%TIME%% and %%DATE%% magic vars in a string with appropriate
    // classed <span> tags, so jquery thingy can replace them later on.

    return (text.replace(/%%TIME%%/,'<span class="magic_time">&nbsp;</span>')
                .replace(/%%DATE%%/,'<span class="magic_date">&nbsp;</span>'));
}

function magic_time() {
    // finds all %%TIME%% and %%DATE%% magic vars which have been replaced
    // by their <span>'d equivalents, and replaces the contents with the current
    // date or time.

    var d = new Date;
    var timestr = ((d.getHours()<10?'0':'') + d.getHours() + ':'
                  +(d.getMinutes()<10?'0':'') + d.getMinutes())
    $('.magic_time').each(function(i){
        this.innerHTML = timestr;
    });
    $('.magic_date').each(function(i){
        this.innerHTML = Date().replace(/:[^:]*$/,'');
    });
    setTimeout(magic_time, 60000);
}

function url_insert(url, data) {
    'use strict';
    // Takes a url with a '-1' in it, and replaces the '-1' with
    // data.  Useful with url_for(...) stored in dynamically generated
    // pages.
    return url.replace(/-1/, data);
}

function faketime(timestring) {
    'use strict';
    // returns time in minutes, either of time NOW, if no argument,
    // or of parsed HH:MM string, if given.

    if (timestring) {
        var split = timestring.match(/(\d\d):(\d\d)/);
        if (('length' in split)&&(split.length==3)) {
            return (60*parseInt(split[1]))+parseInt(split[2]);
        } else {
            console.log ('invalid time: ' + JSON.stringify(timestring));
            return 0;
        }
    } else {
        var now = new Date();
        return (60*now.getHours())+now.getMinutes();
    }
}

function restriction_relevant(now, restriction) {
    // returns True if we're curently within a time restriction's jurisdiction, else False;

    var start = faketime(restriction.start);
    var end = faketime(restriction.end);

    return ((start<now)&&(now<end));
}

function any_relevent_restrictions(post) {
    // returns True if *any* time restriction catches the current time.

    var now = faketime();
    for (var i in post.time_restrictions) {
        if (restriction_relevant(now, post.time_restrictions[i])) {
            return true;
        }
    }

    return false;
}

function reload_page() {
    $.get(document.URL, function() { window.location.reload(); });
    // and if that doesn't work, we'll try again later:
    setTimeout(reload_page, REFRESH_PAGE_TIMER);
}

setTimeout(reload_page, REFRESH_PAGE_TIMER);
setTimeout(magic_time, 2000);
