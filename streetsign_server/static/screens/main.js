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
    screens output, main javascript control system.

*************************************************************/

function addZone(container, obj) {
    "use strict";
    // adds an object into the window zones list,
    // and gives it an element within the container for filling with stuff.

    var csspairs = [], i;
    // temporary!:

    if (!obj.hasOwnProperty('type')) {
        obj.type = 'fade';
    }

    window.zones.push(obj);
    obj.el = $(zone_html(obj.name, obj.top, obj.left, obj.bottom, obj.right, obj.css, obj.type))
              .prependTo(container)[0];

    //obj.classes.map(function(x){ $(obj.el).addClass(x);});
    //alert(obj.classes);
    if (obj.hasOwnProperty('color')) {
        $(obj.el).css('color', obj.color);
    }

    try {
        // this is 'tried' as we aren't sure if the data is valid CSS!
        csspairs = obj.css.split(/[\n;]+/).map(function (x) {
                                           var y = x.match(/^(.*):(.*)$/);
                                           return [y[1].trim(), y[2].trim()]; });
    }catch (ignore){}

    for (i=0; i<csspairs.length;i += 1) {
        $(obj.el).css(csspairs[i][0], csspairs[i][1]);
    }

    //obj.el.innerHTML = '<div>'+obj.el.innerHTML + '<br/>(initialising)</div>';
}

function get_posts_length(zone) {
    "use strict";

    try {
        if (zone.posts.length > 0) {
            return zone.posts.length;
        }
    } catch (ignore) {}

    return 0;
}

function next_post(zone) {
    "use strict";
    /******************************
     * start of new code for time restrictions...
     ******************************/

    var appendlist = [];
    var nextpost = false;
    var thispost;

    var call_me_again = function () { next_post(zone); };
    var make_remove_el = function (post) { return function () { post._el.remove(); }; };

    if ((!zone.hasOwnProperty("posts"))||(zone.posts.length === 0)) {
        // no posts!
        zone.current_post = false;
        setTimeout(call_me_again, zone.no_posts_wait);
        console.log('no posts for '+ zone.name + '!');
        return;
    }

    while (zone.posts.length > 0) {
        thispost = zone.posts.shift();

        if (thispost.hasOwnProperty('delete_me')){
            // it's popped!
            post_fadeout(thispost, zone.fadetime, make_remove_el(thispost));

            console.log(zone.name + '|setting delete_me flag on post:'+ thispost.id);
            continue;
        }

        if (thispost.time_restrictions_show) {
            if (any_relevent_restrictions(thispost)) {
                // we have a winner!
                nextpost = thispost;
                appendlist.push(thispost);
                console.log('Going to show post:' + nextpost.id);
                break;
            }

            appendlist.push(thispost);

        } else {
            if (any_relevent_restrictions(thispost)) {
                appendlist.push(thispost);
                //continue;
            } else {
                // we have a winner!
                nextpost = thispost;
                appendlist.push(thispost);
                break;
            }
        }
    }
    // add delayed posts (including new 'thispost') on to the end of the queue.
    zone.posts = zone.posts.concat(appendlist);

    if (nextpost) {
        if ((!zone.hasOwnProperty('current_post'))||(zone.current_post === false)) {
            // first post!
            zone.current_post = nextpost;
            post_fadein(zone.current_post, zone.fadetime);

            if (post_types[nextpost.type].hasOwnProperty('display')) {
                post_types[nextpost.type].display(nextpost);
            }

            zone.next_post_timer = setTimeout(call_me_again, nextpost.display_time);
            return;

        }

        //if ((nextpost.id === zone.current_post.id)&&(zone.type !== 'scroll')) {
        if (nextpost.id === zone.current_post.id) {
            // this is the only valid post!
            zone.next_post_timer = setTimeout(call_me_again, nextpost.display_time);
            console.log('only this post is available');
            return;
        }

        // if it's not return'd already, then we have a new post to fade to. hurrah!

        post_fadeout(zone.current_post, zone.fadetime, function () {

            if (post_types[zone.current_post.type].hasOwnProperty('hide')) {
                post_types[zone.current_post.type].hide(zone.current_post);
            }

            zone.current_post = nextpost;
            post_fadein(zone.current_post, zone.fadetime);

            try {
                if (post_types[nextpost.type].hasOwnProperty('display')) {
                    post_types[nextpost.type].display(nextpost);
                }
            } catch (e) {
                console.log('ERROR:wrong type:' + nextpost.type);

            }

            zone.next_post_timer = setTimeout(call_me_again, nextpost.display_time);
        });

        return;
    }

    // if we've got this far, then it didn't return earlier with a next post. so...
    // no posts currently allowed!
    if (zone.current_post) {
        post_fadeout(zone.current_post, zone.fadetime, function() {
            if (! zone.current_post) {
                console.log('gone!');
                return;
            }
            if (post_types[zone.current_post.type].hasOwnProperty('hide')) {
                post_types[zone.current_post.type].hide(zone.current_post);
            }

        });

    }
    zone.current_post = false;
    zone.next_post_timer = setTimeout(call_me_again, zone.no_posts_wait);
    console.log('no posts currently valid in zone' + zone.name + '! : ' + JSON.stringify(zone.posts));
    return;

}

function update_screen(screen_data, element) {
    'use strict';
    console.log('getting screen updates...');

    var update = function(data) {
        if (data.md5 === screen_data.md5) {
            setTimeout(function(){update_screen(screen_data, element);}, 12000);
        } else {
            // The md5 is different! we should do some updates!
            // TODO: proper reloading, including pre-downloading background
            //       images before displaying them, updating zone feeds, etc.
            reload_page();
        }
    };

    $.getJSON('/screens/json/' +  screen_data.id + '/' + screen_data.md5, update);

    // And for now, since there isn't really anywhere better, lets also
    // tell all external sources to update if they need to.
    $.getJSON('/external_data_sources/');
}

function background_from_value(text) {
    'use strict';
    if (text.indexOf('.') === -1) {
        // not a filename.
        return text;
    }

    // TODO: load this URL from somewhere!
    return 'url(/static/user_files/' + text + ')';
}

function make_updater(z){
    'use strict';
    // Returns the 'update' closure, a function which is called
    //    when we get new data (posts) from the server, and adds
    //    them into a zone. Captures zone (z) within the closure,
    //    so it can be passed to the $.getJSON(...) callback.
    var zone = z;
    return function (data) {
        var new_post_ids = [], current_post_ids = [], posts_to_pop = [], new_data, i, n;
        var do_next_post = function() { next_post(zone); };
        var arrId = -1;

        //zone.el.innerHTML = data.posts.length;
        if (! zone.hasOwnProperty('posts')) {zone.posts = [];}

        // what posts are in the new list?

        for (i=0; i < data.posts.length; i += 1){
            new_post_ids.push(data.posts[i].id);
        }

        // what posts are currently in the zone?

        for (i=0; i < zone.posts.length; i += 1){
            if ( i > zone.posts.length) {
                console.log('oh no. ' + i + ' > ' + zone.posts.length);
            }

            arrId = $.inArray(zone.posts[i].id, new_post_ids);
            // keep current posts, and delete no-longer needed posts:
            //
            if (arrId !== -1) {
                current_post_ids.push(zone.posts[i].id);
                // update post with all info from server, in case stuff has changed.
                zone.posts[i].time_restrictions_show = data.posts[arrId].time_restrictions_show;
                zone.posts[i].time_restrictions = data.posts[arrId].time_restrictions;
                // Maybe better not ?
                //
                if (JSON.stringify(zone.posts[i].content) !== JSON.stringify(data.posts[arrId].content)) {
                    console.log('differ!');
                    console.log (zone.posts[i].content);
                    console.log (data.posts[arrId].content);
                    zone.posts[i].content = data.posts[arrId].content;
                    if (zone.current_post === i) {
                        post_fadeout(zone.posts[i], zone.fadetime, function() {
                            zone.posts[i].remove();
                            });
                    }
                    console.log("replacing content in post:" + zone.posts[i].id);
                    zone.posts[i]._el = post_types[zone.posts[i].type].render(zone.el, zone.posts[i])[0];
                    if (zone.current_post === i) {
                        post_fadein(zone.posts[i], zone.fadetime );
                    }
                }
                if (zone.type !== 'scroll') {
                    zone.posts[i].display_time = data.posts[arrId].display_time;
                }
            } else {

                // the current post id is NOT in the list of new posts from the server.
                // so we should delete it from the list here.

                console.log('marking post for delete:' + zone.posts[i].id);
                zone.posts[i].delete_me = true;

                // if we're currently displaying this post, then bring forward
                // the timeout to 1 second from now (should be long enough to
                // finish loading any other posts...)
                if (zone.current_post === zone.posts[i]) {
                    console.log(zone.name + '|bringing forward next post timer');
                    clearTimeout(zone.next_post_timer);
                    zone.next_post_timer = setTimeout(do_next_post, 1000);
                } else {
                    console.log(zone.name + '|adding to popqueue:' + zone.posts[i].id);
                    //zone.posts.pop(i);
                    posts_to_pop.push(i);
                }
            }
        }

        for (i=0; i<posts_to_pop.length; i++) {
            console.log(posts_to_pop[i], zone.posts.length);
            console.log(zone.name + '|popping!:' + zone.posts[posts_to_pop[i]].id);
            zone.posts.pop(posts_to_pop[i]);
        }

        // add new posts to the list!
        for (i=0; i<data.posts.length; i += 1) {
            new_data = data.posts[i];

            if (!($.inArray(new_data.id, current_post_ids) !== -1)) {

                n = zone.posts.push(new_data) - 1;
                console.log('adding:' + n + ': length:' + zone.posts.length);

                zone.posts[n].zone = zone;
                zone.posts[n]._el =
                    post_types[zone.posts[n].type].render(zone.el, zone.posts[n])[0];
            }
        }
    }; // end of closure...
}

function update_zones_posts() {
    'use strict';
    var i, zone, update;

    for (i=0; i<window.zones.length; i += 1) {
        zone = window.zones[i];
        update = make_updater(zone);

        $.getJSON(url_insert(POSTS_URL, JSON.stringify(zone.feeds)), update);
    }
    // TODO: get this value from somewhere:
    setTimeout(update_zones_posts, UPDATE_ZONES_TIMER);
}

function init_screen(screen_data, element) {
    'use strict';

    var keyname, zone;

    $(element).css('background-image', background_from_value(screen_data.background));

    // copy default values into all zones.
    // this could probably be done better with prototypes...

    for (zone=0; zone<screen_data.zones.length;zone += 1) {
        // copy 'default' data in, if it needs it ONLY.
        for (keyname in screen_data.defaults) {
            if (screen_data.defaults.hasOwnProperty(keyname)) {
                if (! screen_data.zones[zone].hasOwnProperty(keyname) ){
                    screen_data.zones[zone][keyname] = screen_data.defaults[keyname];
                }
            }
        }
        addZone(element, screen_data.zones[zone]);
    }

    update_zones_posts();
    setTimeout(function(){update_screen(screen_data, element);}, 3000);
}

function start_zones_scrolling() {
    'use strict';
    var i;

    for (i=0; i<window.zones.length; i += 1) {
        next_post(window.zones[i]);
    }
}
