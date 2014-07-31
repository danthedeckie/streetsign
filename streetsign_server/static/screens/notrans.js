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

    return ('<div id="_zone_'+id+'" class="zone zone_'+type+'" style="'
            +'left:' + left
            +';right:' + right
            +';bottom:' + bottom
            +';top:' + top
            +';' + css.replace(/"/g,"'")
            + '"></div>');
}

/***************************************************************************/

// These are the different kinds of zones, fading or scrolling only for now.
// To add new zone types, all you need to do is add them in here, and in
// the list of ZONE_TYPES in screen_editor.html

var zone_types = {
    fade: {
        start: function (post, cb){
            "use strict";

            // TODO: in zone setup, set zone > post opacity fadetimes...
            post.el.style.opacity = 1.0;
            setTimeout(cb, post.zone.fadetime);
        },
        stop: function (post, cb){
            "use strict";
            post.el.style.opacity = 0;
            setTimeout( function () {
                //post.el.style.display = 'none';
                cb && cb();
            }, post.zone.fadetime);
        }
    },
   scroll: {
        start: function (post, cb) {
            "use strict";

            var stylesheet,
                prefix = "",
                css,
                post_width = post.el.scrollWidth,
                total_distance = post.zone.width + post_width,
                current_left = post.zone.width,
                end_left = 0 - post.width,
                start_time = null,
                mover = (function(timestamp) {
                    var progress, new_left;

                    if (start_time === null) start_time = timestamp;
                    progress = (timestamp - start_time);

                    if (current_left > end_left) {
                        new_left = (total_distance / post.display_time) * (post.display_time - progress) - post_width;
                        if (new_left < current_left -1) {
                            current_left = new_left;
                        } else if (new_left > current_left) {
                            return;
                        }
                        post.el.style.left = current_left + 'px';
                        //requestAnimationFrame(mover);
                        //setTimeout(function(){requestAnimationFrame(mover)},1000);
                        requestAnimationFrame(mover);
                    }
                });

            // Why does this need to be set here? it seems like the
            // previous setting in main.js (Zone.prototype.addPost)
            // gets an incorrect value...

            post.width = post.el.scrollWidth;

            requestAnimationFrame(mover);

            post.el.style.display = 'block';
            post.el.style.opacity = 1;

            post.display_time = (post.width + post.zone.width) * 14;

            // and call the 'after starting' callback:
            cb && cb();

            },
        stop: function (post, cb) {
            "use strict";

            //post.zone.el.style.opacity = 0;

            setTimeout( function () {
                //post.el.style.display = 'none';

                post.el.style.webkitAnimation = "";
                post.el.style.mozAnimation = "";
                post.el.style.animation = "";

                post.el.style.opacity = 0;
                //post.scroll_stylesheet.remove()
                //delete post.scroll_stylesheet;

               post.zone.el.style.opacity = 1.0;
                cb && cb()
            }, 1001);
        }
    }
    };


function post_fadein(post, cb) {
    "use strict";

    return (zone_types[post.zone.type]||zone_types.fade).start(post, cb);
}

function post_fadeout(post, cb) {
    "use strict";

    return (zone_types[post.zone.type]||zone_types.fade).stop(post, cb);
}
function post_display(post) {
    "use strict";
    if (post_types[post.type].hasOwnProperty('display')) {
        post_types[post.type].display(post);
    }
}

function post_hide(post) {
    "use strict";
    if (post_types[post.type].hasOwnProperty('hide')) {
        post_types[post.type].hide(post);
    }
}

function post_render(post_data, zone) {
    "use strict";
    return post_types[post_data.type].render(zone.el, post_data)[0];
}
