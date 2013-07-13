// TODO: get these from somewhere?
//'use strict';
UPDATE_ZONES_TIMER = 6000; // how often to check for new posts?

// These will eventually be loaded from their plugin files, rather than being
// hard-coded in here.

post_renderers = {
    html: function(zone, data) {
        console.log('making html');
        return $('<div class="post post_html">' + data.content.content + '</div>')
            .prependTo(zone);
    },
    text: function(zone, data) {
        console.log('making text');
        return ($('<div class="post post_text"><pre>' 
                  + data.content.content 
                  + '</pre></div>')
            .prependTo(zone));
    },
    image: function(zone, data) {
        console.log('making img');
        console.log(data.content.file_url);
        return ($('<div class="post post_image"><img src="'
                 + data.content.file_url
                 + '" style="width:100%;height:auto;" /></div>')
            .prependTo(zone));
    }
};

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

    window.zones.push(obj);
    obj.el = $(zone_html(obj.name, obj.top, obj.left, obj.bottom, obj.right))
              .prependTo(container)[0];

    $(obj.el).addClass(obj.classes);
    $(obj.el).attr('css',obj.css);

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
     * start of new code for time restrictions... this whole function
     * must be rewritten totally.  This gives the rough idea how to do it.
     ******************************
    var CURR_POST = -1;
    var NEXT_POST = -1;
    var TOTAL_POSTS = get_posts_length(zone);

    if ('current_post' in zone) {
        CURR_POST = zone.current_post;
        NEXT_POST = CURR_POST + 1;
    } else {
        // current post not set up yet. so set it to -1...
        zone.current_post = CURR_POST;
    }

    while ( NEXT_POST != CURR_POST ) {
        // which means if current_post is -1, we don't bother with anything.

        // wrap around:
        if (NEXT_POST >= TOTAL_POSTS) { NEXT_POST = 0 };

        // TODO: go through all time restrictions of post, compare to current time,
        //       and if we're hit by them, either continue, or break.

        // let's try the next one then...
        NEXT_POST++;
    }

    // either we now have a next post, or else it is the same as the current post.
    **************************************************
    * end of new code. TODO TODO TODO.
    **************************************************
    */

    // scroll through the posts loaded into a zone.

    // if it's not already scrolling, start!
    if (!('current_post' in zone))
        zone.current_post = -1;
    else
        // let's first sort out the currently displayed post:

        if ('posts' in zone) {
            // there are some posts.
            if (zone.current_post > -1) {
                // we are actually currently displaying something.

                if (zone.posts[zone.current_post].delete_me == true) {
                    // if the post just faded out is marked for deletion,
                    // then fade it out, and delete it.

                    $(zone.posts[zone.current_post]._el).fadeOut();
                    console.log('deleting current post:' + zone.current_post)
                    zone.posts.pop(zone.current_post);
                } else {
                    if (zone.posts.length > 1) {
                        // it's not marked for deletion, and there are
                        // other posts to display, so fade it out.
                        $(zone.posts[zone.current_post]._el).fadeOut();
                    }
                }
            }
        }

    // let's move on to the next post in the list.
    zone.current_post++;
    if ((!('posts' in zone)) || (zone.posts.length == 0)) {
        // there are no posts! I guess we'll sit around and wait for some.
        zone.current_post = -1;
        setTimeout(function(){next_post(zone);}, zone.no_posts_wait);
        console.log('no posts!');
        return;
        }

    // wrap around.
    if (zone.posts.length <= zone.current_post) {
        zone.current_post = 0;
    }
    //zone.el.innerHTML = zone.posts[zone.current_post].content.content;
    $(zone.posts[zone.current_post]._el).fadeIn();
    //zone.el.innerHTML = 'postid:' + zone.current_post;
    if ('display_time' in zone.posts[zone.current_post]) {
        zone.next_post_timer = setTimeout(function(){next_post(zone);}, zone.posts[zone.current_post].display_time);
    } else {
        zone.next_post_timer = setTimeout(function(){next_post(zone);}, zone.post_time);
    }
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
        console.log('adding zone:' + screen_data.zones[z].name);
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
            // keep current posts, and delete no-longer needed posts:
            if ($.inArray(zone.posts[i].id, new_posts)!=-1) {
                current_posts.push(zone.posts[i].id);
            } else {
                console.log('marking post for delete:' + i);
                zone.posts[i].delete_me = true;

                // if we're currently displaying this post, then bring forward
                // the timeout to 1 second from now (should be long enough to
                // finish loading any other posts...)
                if (zone.current_post == i) {
                    console.log('bringing forward next post timer')
                    clearTimeout(zone.next_post_timer);
                    setTimeout(function(){next_post(zone);}, 1000);
                } else {
                    console.log('deleting post:' + i)
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
                    post_renderers[zone.posts[n].type](zone.el, zone.posts[n]);
                var zone_height = $(zone.el).height();
                var my_height =el.height();
                if (my_height < zone_height) {
                    el.css('top', (zone_height/2)-(my_height/2));
                }
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
