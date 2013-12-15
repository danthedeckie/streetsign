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

function zone(container, obj) {
    // adds an object into the window zones list,
    // and gives it an element within the container for filling with stuff.

    var csspairs = [];
    // temporary!:

    if (! 'type' in obj) {
        obj.type='fade';
    }

    window.zones.push(obj);
    obj.el = $(zone_html(obj.name, obj.top, obj.left, obj.bottom, obj.right, obj.css, obj.type))
              .prependTo(container)[0];

    //obj.classes.map(function(x){ $(obj.el).addClass(x);});
    //alert(obj.classes);
    if ('color' in obj) {
        $(obj.el).css('color', obj.color);
    }

    try {
        // this is 'tried' as we aren't sure if the data is valid CSS!
        csspairs = obj.css.split(/[\n;]+/).map(function (x) {
                                           var y = x.match(/^(.*):(.*)$/);
                                           return [y[1].trim(),y[2].trim()] } );
    }catch(e){};

    for (var i in csspairs) {
        $(obj.el).css(csspairs[i][0], csspairs[i][1]);
    };

    //obj.el.innerHTML = '<div>'+obj.el.innerHTML + '<br/>(initialising)</div>';
}

function get_posts_length(zone) {
    try {
        if (zone.posts.length > 0) {
            return zone.posts.length;
        } else {
            return 0;
        }
    } catch (e) {
        return 0;
    }
}

function next_post(zone) {
    /******************************
     * start of new code for time restrictions...
     ******************************/

    var appendlist = [];
    var nextpost = false;

    if ((!('posts' in zone))||(zone.posts.length==0)) {
        // no posts!
        zone.current_post = false;
        setTimeout(function(){next_post(zone);}, zone.no_posts_wait);
        console.log('no posts for '+ zone.name + '!');
        return;
    }

    while (zone.posts.length > 0) {
        var thispost = zone.posts.shift();

        if ('delete_me' in thispost){
            // it's popped!
            post_fadeout(thispost, zone.fadetime, function() {
                thispost._el.remove();
                });
            console.log('deleting element:'+ thispost.id);
            continue;
        }
        if (thispost.time_restrictions_show) {
            if (any_relevent_restrictions(thispost)) {
                // we have a winner!
                nextpost = thispost;
                appendlist.push(thispost);
                console.log('Going to show post:' + nextpost.id);
                break;
            } else {
                appendlist.push(thispost);
                //continue;
            }
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
        if (!('current_post' in zone)||(zone.current_post == false)) {
            // first post!
            zone.current_post = nextpost;
            post_fadein(zone.current_post, zone.fadetime);

            if ('display' in post_types[nextpost.type]) {
                post_types[nextpost.type].display(nextpost);
            }

            setTimeout(function(){next_post(zone);}, nextpost.display_time);
            return;

        }
        if ((nextpost.id == zone.current_post.id)&&(zone.type!='scroll')) {
            // this is the only valid post!
            setTimeout(function(){next_post(zone);}, nextpost.display_time);
            console.log('only this post is available');
            return;
        } else {
            // we have a new post to fade to. hurrah.
            post_fadeout(zone.current_post, zone.fadetime, function() {

                if ('hide' in post_types[zone.current_post.type]) {
                    post_types[zone.current_post.type].hide(zone.current_post);
                }

                zone.current_post = nextpost;
                post_fadein(zone.current_post, zone.fadetime);

                try {
                if ('display' in post_types[nextpost.type]) {
                    post_types[nextpost.type].display(nextpost);
                }
                } catch (e) {

                    console.log('ERROR:wrong type:' + nextpost.type);

                }

                setTimeout(function(){next_post(zone);}, nextpost.display_time);
            });
            return;
        }
    } else {
        // no posts currently allowed!
        if (zone.current_post) {
            post_fadeout(zone.current_post, zone.fadetime, function() {
                if ('hide' in post_types[zone.current_post.type]) {
                    post_types[zone.current_post.type].hide(zone.current_post);
                }

            });

        }
        zone.current_post = false;
        setTimeout(function(){next_post(zone);}, zone.no_posts_wait);
        console.log('no posts currently valid in zone'+zone.name+'! : ' + JSON.stringify(zone.posts));
        return;
    }

    // I have no clue how we could have got here, but if we have, by some
    // edgecase, then delay and call again.

    console.log('Somehow at the end of the next_post function. odd');
    setTimeout(function(){next_post(zone);}, zone.no_posts_wait);


}

function update_screen(screen_data, element) {
    'use strict';
    console.log('getting screen updates...');

    var update = function(data) {
        if (data.md5 == screen_data.md5) {
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
    if (text.indexOf('.') == -1) {
        // not a filename.
        return text;
    } else {
        // TODO: load this URL from somewhere!
        return 'url(/static/user_files/' + text + ')';
    }
}

function init_screen(screen_data, element) {

    $(element).css('background-image', background_from_value(screen_data.background));

    for (var z in screen_data.zones) {
        // copy 'default' data in, if it needs it ONLY.
        for (var d in screen_data.defaults) {
            if (! (d in screen_data.zones[z])){
                screen_data.zones[z][d] = screen_data.defaults[d];
            }
        }
        zone(element, screen_data.zones[z]);
    }

    update_zones_posts();
    setTimeout(function(){update_screen(screen_data, element);}, 3000);
}

function start_zones_scrolling() {
    for (var i=0;i<window.zones.length;i++) {
        next_post(window.zones[i]);
    }
}


function make_updater(z){
    // Returns the 'update' closure, a function which is called
    //    when we get new data (posts) from the server, and adds
    //    them into a zone. Captures zone (z) within the closure,
    //    so it can be passed to the $.getJSON(...) callback.
    var zone = z;
    return function(data) {
        //zone.el.innerHTML = data.posts.length;
        if (!('posts' in zone)){zone.posts = [];}

        // what posts are in the new list?

        var new_posts = [];
        for (var i in data.posts){
            new_posts.push(data.posts[i].id);
        }
        // what posts are currently in the zone?
        var current_posts = [];
        for (var i in zone.posts){
            var arrId = $.inArray(zone.posts[i].id, new_posts);
            // keep current posts, and delete no-longer needed posts:
            if (arrId !=-1) {
                current_posts.push(zone.posts[i].id);
                // update post with all info from server, in case stuff has changed.
                zone.posts[i].time_restrictions_show = data.posts[arrId].time_restrictions_show;
                zone.posts[i].time_restrictions = data.posts[arrId].time_restrictions;
                // Maybe better not ?
                if (JSON.stringify(zone.posts[i].content) != JSON.stringify(data.posts[arrId].content)) {
                    zone.posts[i].content = data.posts[arrId].content;
                    if (zone.current_post == i) {
                        post_fadeout(zone.posts[i], zone.fadetime, function() {
                            zone.posts[i].remove();
                            });
                    }
                    zone.posts[i]._el = post_types[zone.posts[i].type].render(zone.el, zone.posts[i])[0];
                    if (zone.current_post == i) {
                        post_fadein(zone.posts[i], zone.fadetime );
                    }
                }
                zone.posts[i].display_time = data.posts[arrId].display_time;
            } else {
                console.log('marking post for delete:' + zone.posts[i].id);
                zone.posts[i].delete_me = true;

                // if we're currently displaying this post, then bring forward
                // the timeout to 1 second from now (should be long enough to
                // finish loading any other posts...)
                if (zone.current_post == zone.posts[i]) {
                    console.log('bringing forward next post timer')
                    clearTimeout(zone.next_post_timer);
                    setTimeout(function(){next_post(zone);}, 1000);
                } else {
                    console.log('deleting post:' + zone.posts[i].id)
                    zone.posts.pop(i);
                }
            }
        }


        // add new posts to the list!
        for (var i in data.posts) {
            var new_data = data.posts[i];
            if (!($.inArray(new_data.id, current_posts)!=-1)) {
                var n = zone.posts.push(new_data) - 1;
                zone.posts[n].zone = zone;
                var el =
                    post_types[zone.posts[n].type].render(zone.el, zone.posts[n]);
                zone.posts[n]._el = el[0];

            }
        }
    }
}

function update_zones_posts() {
    for (var i in window.zones) {
        var zone = window.zones[i];
        var update = make_updater(zone);

        $.getJSON(url_insert(POSTS_URL, JSON.stringify(zone.feeds)), update);
    }
    // TODO: get this value from somewhere:
    setTimeout(update_zones_posts, UPDATE_ZONES_TIMER);
}
