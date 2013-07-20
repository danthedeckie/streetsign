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
    screens output, main javascript control system.

*************************************************************/

// TODO: get these from somewhere?
//'use strict';
UPDATE_ZONES_TIMER = 6000; // how often to check for new posts?
REFRESH_PAGE_TIMER = 3600000; // how often to reboot the page? this is every hour...

window.post_types = {};

function magic_vars(text) {
    return (text.replace(/%%TIME%%/,'<span class="magic_time">&nbsp;</span>')
                .replace(/%%DATE%%/,'<span class="magic_date">&nbsp;</span>'));
}

function magic_time() {
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
setTimeout(magic_time, 2000);

function url_insert(url, data) {
    // Takes a url with a '-1' in it, and replaces the '-1' with
    // data.  Useful with url_for(...) stored in dynamically generated
    // pages.
    return url.replace(/-1/, data);
}

// Where to store all zones to be updated & stuff.
window.zones = [];

// Returns the HTML for a zone area
// TODO: This should really be templated out.
function zone_html(id, top, left, bottom, right) {
    return ('<div id="_zone_'+id+'" class="zone" style="'
            +'left:' + left
            +';right:' + right
            +';bottom:' + bottom
            +';top:' + top + '"></div>');
}

function zone(container, obj) {
    // adds an object into the window zones list,
    // and gives it an element within the container for filling with stuff.

    var csspairs = [];

    window.zones.push(obj);
    obj.el = $(zone_html(obj.name, obj.top, obj.left, obj.bottom, obj.right, obj.css))
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

function faketime(timestring) {
    'use strict';
    // returns time in minutes, either of time NOW, if no argument,
    // or of parsed HH:MM string.

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
            $(thispost._el).fadeOut().remove();
            console.log('deleing element:'+ thispost.id);
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
            $(zone.current_post._el).fadeIn(zone.fadetime);

            if ('display' in post_types[nextpost.type]) {
                post_types[nextpost.type].display(nextpost);
            }

            setTimeout(function(){next_post(zone);}, nextpost.display_time);
            return;

        }
        if (nextpost.id == zone.current_post.id) {
            // this is the only valid post!
            setTimeout(function(){next_post(zone);}, nextpost.display_time);
            console.log('only this post is available');
            return;
        } else {
            // we have a new post to fade to. hurrah.
            $(zone.current_post._el).fadeOut(zone.fadetime, function() {

                if ('hide' in post_types[zone.current_post.type]) {
                    post_types[zone.current_post.type].hide(zone.current_post);
                }

                zone.current_post = nextpost;
                $(zone.current_post._el).fadeIn(zone.fadetime);

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
            $(zone.current_post._el).fadeOut(zone.fadetime, function() {
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

function init_screen(screen_data, element) {

    $(element).css('background-image',screen_data.background);

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
                zone.posts[i].time_restrictions_show = data.posts[arrId].time_restrictions_show;
                zone.posts[i].time_restrictions = data.posts[arrId].time_restrictions;
                // Maybe better not ?
                if (JSON.stringify(zone.posts[i].content) != JSON.stringify(data.posts[arrId].content)) {
                    zone.posts[i].content = data.posts[arrId].content;
                    if (zone.current_post == i) {
                        $(zone.posts[i]._el).fadeOut().remove()
                    }
                    zone.posts[i]._el = post_types[zone.posts[i].type].render(zone.el, zone.posts[i])[0];
                    if (zone.current_post == i) {
                        $(zone.posts[i]._el).fadeIn();
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

function reload_page() {
    $.get(document.URL, function() { window.location.reload(); });
    // and if that doesn't work, we'll try again later:
    setTimeout(reload_page, REFRESH_PAGE_TIMER);
}
setTimeout(reload_page, REFRESH_PAGE_TIMER);
