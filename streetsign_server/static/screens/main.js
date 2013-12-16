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
    // This function is called once a post has been shown for long enough.
    // It fades out the old post, fades in the new one, and schedules itself
    // to run again when the next one has been up for long enough.
    //
    // When it goes through the posts, determining which post to show next,
    // it automatically prunes out any which are marked for deletion by the
    // post list updater.
    //
    // If there are no posts, then it schedules itself to run later, without
    // doing anything. (Sit around and wait for something to do).

    var appendlist = [];
    var nextpost = false;
    var thispost;

    // call this function again, used as a callback:
    var call_me_again = function () { next_post(zone); };

    // return a function for removing an element from the DOM.
    var make_remove_el = function (post) { return function () { post._el.remove(); }; };

    // if there are no posts, then schedule to call this again later, and return:

    if ((!zone.hasOwnProperty("posts"))||(zone.posts.length === 0)) {
        // no posts!
        zone.current_post = false;
        setTimeout(call_me_again, zone.no_posts_wait);
        console.log('no posts for '+ zone.name + '!');
        return;
    }

    // go through all the current posts, move any which aren't tagged for deletion
    // onto a new "appendlist". shunt any posts which are time restricted to the end
    // of the list, so they won't get shown now, but stay in the list.

    while (zone.posts.length > 0) {

        thispost = zone.posts.shift();

        // if it's sheduled for deletion, DON'T add it to the new list, but fade it out
        // (if it is visible) and delete the element.

        if (thispost.hasOwnProperty('delete_me')){
            // it's popped!
            post_fadeout(thispost, zone.fadetime, make_remove_el(thispost));

            console.log(zone.name + '|dropping post from feed (and removing el):'+ thispost.id);
            continue;
        }

        // fine, it's not scheduled for deletion, so stuff it on the appendlist
        // stack:

        appendlist.push(thispost);

        // check time restrictions.  If they allow this post to be shown, then we'll
        // use it as the next one to display!

        if (thispost.time_restrictions_show) {
            if (any_relevent_restrictions(thispost)) {
                // we have a winner!
                nextpost = thispost;
                break;
            }
        } else { // inverse restrictions...
            if (!(any_relevent_restrictions(thispost))) {
                // we have a winner!
                nextpost = thispost;
                break;
            } 
        }

        // alas, the time restrictions didn't let this post get selected. So
        // wrap around to the next post...
    }

    // add delayed posts (including new 'thispost') on to the end of the queue.
    zone.posts = zone.posts.concat(appendlist);

    //////////////////////////////////////////////////////////////////////////
    //
    // if a nextpost was selected, then let's display it.

    if (nextpost) {

        // if there is no current post to fade from:

        if ((!zone.hasOwnProperty('current_post'))||(zone.current_post === false)) {
            // first post!
            zone.current_post = nextpost;
            post_fadein(zone.current_post, zone.fadetime);

            // posttype 'display' callback:
            if (post_types[nextpost.type].hasOwnProperty('display')) {
                post_types[nextpost.type].display(nextpost);
            }

            zone.next_post_timer = setTimeout(call_me_again, nextpost.display_time);
            return;

        }

        // if this post is *already* the current post:
        
        if (nextpost.id === zone.current_post.id) {
            // same post!
            zone.next_post_timer = setTimeout(call_me_again, nextpost.display_time);
            console.log('only this post is available');
            return;
        }

        // if it's not return'd already, then we have a new post to fade to.

        post_fadeout(zone.current_post, zone.fadetime, function () {
            // callback *after* the previous post has faded out:

            // posttype 'hide' callback:
            if (post_types[zone.current_post.type].hasOwnProperty('hide')) {
                post_types[zone.current_post.type].hide(zone.current_post);
            }

            // set current post, and fade it in:

            zone.current_post = nextpost;
            post_fadein(zone.current_post, zone.fadetime);

            // posttype 'display' callback:
            if (post_types[nextpost.type].hasOwnProperty('display')) {
                post_types[nextpost.type].display(nextpost);
            }

            // schedule this function to run again, once the post has been
            // display'd for as long as it wants to be:

            zone.next_post_timer = setTimeout(call_me_again, nextpost.display_time);
        });

        // My work here is done.

        return;
    }

    // if we've got this far, then it didn't return earlier with a next post. so...
    // no posts currently allowed!
    if (zone.current_post) {
        // ok, no posts allowed, but there *is* a current post.
        // let's get rid of it.

        post_fadeout(zone.current_post, zone.fadetime, function() {
            // callback once the post is faded out...

            if (! zone.current_post) {
                console.log('gone!');
                return;
            }

            // posttype 'hide' callback:
            if (post_types[zone.current_post.type].hasOwnProperty('hide')) {
                post_types[zone.current_post.type].hide(zone.current_post);
            }

        });

    }

    zone.current_post = false;
    zone.next_post_timer = setTimeout(call_me_again, zone.no_posts_wait);
    console.log('no posts currently valid in zone' + zone.name + '!');
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

function update_post_data(post, update_data){
    'use strict';
    // update the data in a post with the new data sent from the server:
    //
    post.time_restrictions_show = update_data.time_restrictions_show;
    post.time_restrictions = update_data.time_restrictions;
    // Maybe better not ?
    if (JSON.stringify(post.content) !== JSON.stringify(update_data.content)) {
        console.log('differ!');
        console.log (post.content);
        console.log (update_data.content);
        post.content = update_data.content;
        if (zone.current_post === i) {
            post_fadeout(post, zone.fadetime, function() {
                post.remove();
                });
        }
        console.log("replacing content in post:" + post.id);
        post._el = post_types[post.type].render(zone.el, post)[0];
        if (zone.current_post === i) {
            post_fadein(post, zone.fadetime );
        }
    }
    if (post.zone.type !== 'scroll') {
        post.display_time = update_data.display_time;
    }
}

function make_updater(z){
    'use strict';
    // Returns the 'update' closure, a function which is called
    //    when we get new data (posts) from the server, and adds
    //    them into a zone. Captures zone (z) within the closure,
    //    so it can be passed to the $.getJSON(...) callback.
    var zone = z;
    return function (data) {
        var new_post_ids = {}, current_post_ids = [], posts_to_pop = [], new_data, i, n;
        var do_next_post = function() { next_post(zone); };
        var arrId = -1;

        if (! zone.hasOwnProperty('posts')) {zone.posts = [];}

        // what posts are in the new list?

        for (i=0; i < data.posts.length; i += 1){
            new_post_ids[data.posts[i].id]=i;
        }

        // what posts are currently in the zone?

        for (i=0; i < zone.posts.length; i += 1){

            // keep current posts, and delete no-longer needed posts:
            if (new_post_ids.hasOwnProperty(zone.posts[i].id)){

                arrId = new_post_ids[zone.posts[i].id];

                // therefore the post IS in the new list of posts from
                // the server.  Let's keep it around then.

                current_post_ids.push(zone.posts[i].id);

                // update post with all info from server, in case stuff has changed.
                update_post_data(zone.posts[i], data.posts[arrId];
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
