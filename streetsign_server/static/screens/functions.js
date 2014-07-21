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
    screens output, generic-ish functions.

*************************************************************/

function nicemap(objects, func) {
    'use strict';
    // a 'map' function which splits each iteration over a new frame,
    // hopefully reducing jank.
    var i=objects.length,
        runner = (function(){
            if (i--) {
                func(objects[i]);
                requestAnimationFrame(runner);
            }
        });
    requestAnimationFrame(runner);
}

function safeGetJSON(url, callback, retry_time=60000) {
    "use strict";
    // simple async JSON request.  Used instead of the jQuery version, which
    // makes about 15 external function calls, delving deeper into the jQuery
    // recursive vortex of confusion.  This simply calls the callback with the
    // JSON data, and if it fails, keeps trying (after a delay).
    //
    // TODO: failure mode callback, and catch failed JSON parsing callback.

    var xhr = new XMLHttpRequest(),
        responder = (function() {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    try {
                        callback(JSON.parse(xhr.responseText));
                    } catch (e) {
                        console.log('Failed to parse response from ' + url + '.' +
                                    'Trying again in ' + (retry_time / 1000) + ' seconds');
                        console.log(e);
                        setTimeout(function() {safeGetJSON(url, callback, retry_time);},
                                   retry_time);
                    }

                } else {
                    console.log('Failed to get ' + url + ' successfully. ' +
                                'Trying again in ' + (retry_time / 1000) + ' seconds.');
                    setTimeout(function() {safeGetJSON(url, callback, retry_time);},
                               retry_time);
                }
            }
        });

    if (callback) {
        xhr.onreadystatechange = responder;
    }

    xhr.open("GET", url, true);
    xhr.send(null);

}


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

    var split, now;

    if (timestring) {
        split = timestring.match(/(\d\d):(\d\d)/);
        if (('length' in split)&&(split.length==3)) {
            return (60*parseInt(split[1]))+parseInt(split[2]);
        } else {
            console.log ('invalid time: ' + JSON.stringify(timestring));
            return 0;
        }
    } else {
        now = new Date();
        return (60*now.getHours())+now.getMinutes();
    }
}

function restriction_relevant(now, restriction) {
    'use strict';
    // returns True if we're curently within a time restriction's jurisdiction, else False;

    var start = faketime(restriction.start);
    var end = faketime(restriction.end);

    return ((start<now)&&(now<end));
}

function any_relevent_restrictions(post) {
    'use strict';

    // returns True if *any* time restriction catches the current time.

    var now = faketime();
    var i;


    for (i=0; i< post.time_restrictions.length; i += 1) {
        if (restriction_relevant(now, post.time_restrictions[i])) {
            if (!thispost.time_restrictions_show) {
                return true;
            }
        }
    }
    return post.time_restrictions_show;
}

function reload_page() {
    'use strict';

    $.get(document.URL, function() { window.location.reload(); });
    // and if that doesn't work, we'll try again later:
    setTimeout(reload_page, REFRESH_PAGE_TIMER);
}

function reduce_font_size_to_fit(inner, outer) {
    'use strict';
    // reduce fontsize until the inner fits within outer.
    // if it's a scrolling zone, then assume almost infinite width...

    var percent = 100;
    var height = 0;
    var zone_height = $(outer).height();
    var zone_width = $(outer).width();
    var i = 100;
    var height = inner.height();
    var width = inner.width();
    var scrolling = (outer[0].className.indexOf("scroll") !== -1);

    if (scrolling) {
        zone_width = 900000;
    }


   // if ((height > zone_height) || (width > zone_width)) {
        while(i > 1){
            height = inner.height();
            width = inner.width();

            i = i / 2;
            if ((height < zone_height) || ((!scrolling) && (width < zone_width))) {
                percent += i;

            } else if ((height > zone_height) || ((!scrolling) && (width > zone_width))) {
                percent -= i;
            }
            inner.css('font-size', percent + '%');
        }
        inner.css('font-size', parseInt(percent) + '%');
        console.log ('reducing font size to ' + parseInt(percent) + '%');
    //}
}

setTimeout(reload_page, REFRESH_PAGE_TIMER);
setTimeout(magic_time, 2000);
