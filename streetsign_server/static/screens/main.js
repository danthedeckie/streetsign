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

// small functions, to go elsewhere:

function cssPairs(cssText) {
    "use strict";
    // given some css as text, return a list of pairs for adding on to an object.

    try {
        // this is 'tried' as we aren't sure if the data is valid CSS!
        return cssText.split(/[\n;]+/).map(function (x) {
                                           var y = x.match(/^(.*):(.*)$/);
                                           return [y[1].trim(), y[2].trim()]; });
    } catch (e) {
        if (cssText) {
            console.log("invalid CSS!");
        }
        return [];
    }
}

function background_from_value(text) {
    "use strict";
    if (text.indexOf('.') === -1) {
        // not a filename.
        return text;
    }

    // TODO: load this URL from somewhere!
    return 'url(/static/user_files/' + text + ')';
}

///////////////////////////////////////////////////////////////////////////////
//
// Zone object:
//

function Zone(container, initial_data) {
    "use strict";

    var i,
        that = this,
        update = function (name, type) {
            if (initial_data.hasOwnProperty(name)) {
                try {
                    that[name] = type(initial_data[name]);
                } catch (ignore) {
                    that[name] = initial_data[name];
                }
            }
        };

    // default "mutable type" properties:
    this.feeds = [];
    this.posts = [];
    this.next_posts = [];

    this.update_cb = make_updater(this);

    // update zone from initial data.
    // this could probably be done better by some ECMA5 function?
    // or even $.extend...
    update('feeds');
    update('color');
    update('name');
    update('type');
    update('fontfamily');

    if (LOCALOPTS.hasOwnProperty('fadetime')) {
        this['fadetime'] = parseInt(LOCALOPTS['fadetime'],10);
    } else {
        update('fadetime', function(x){return parseInt(x, 10);});
    }

    this.feedsurl = url_insert(POSTS_URL, JSON.stringify(this.feeds));

    // tell the world that we're making new posts:
    console.log(this.type);

    // render the new zone element:
    // (zone_html is defined in the template-specific javascript file)
    this.el = $(zone_html(initial_data.name,
                          initial_data.top,
                          initial_data.left,
                          initial_data.bottom,
                          initial_data.right,
                          initial_data.css,
                          initial_data.type)).prependTo(container)[0];

    // and store width and height for less layout thrashing later on...

    this.height = this.el.offsetHeight;
    this.width = this.el.scrollWidth;

    $(this.el).css('font-size', $(this.el).height() + 'px');

    $(this.el).css('color', that['color']);
    if (that['fontfamily']) {
        $(this.el).css('font-family', that['fontfamily']);
    }

}

Zone.prototype = {
    // default "immutable type" properties:
    type: 'fade',
    color: 'white',
    post_time: 4000,
    fadetime: 500,
    update_zones_timer: 10000,
    no_posts_wait: 10000,
    current_post: false,
    current_post_index: -1,

    // methods:
    addPost: function (new_data) {
        "use strict";
        new_data.zone = this;
        new_data.el =
            post_types[new_data.type].render(this.el, new_data)[0];
        new_data.width = new_data.el.scrollWidth;
        new_data.height = new_data.el.scrollHeight;

        // TODO is this right?
        new_data.el.style.transition = "opacity 0." + this.fadetime + "s";
        new_data.el.style.webkitTransition = "opacity 0." + this.fadetime + "s";
        //new_data.el.style.display = "none";
        this.posts.push(new_data);

    },

    delPost: function (index) {
        "use strict";
    },

    updatePost: function (post, newData) {
        'use strict';
        // update the data in a post with the new data sent from the server:
        var that = this;

        post.time_restrictions_show = newData.time_restrictions_show;
        post.time_restrictions = newData.time_restrictions;

        if (post.changed !== newData.changed) {

            post.content = newData.content;

            if (this.current_post.id === post.id) {
                that.el.style.opacity = 0;
                //$(that.el).css('opacity', 0);
                setTimeout( function () {
                    var old_opacity = $(post.el).css('opacity');
                    console.log("replacing content in live post");
                    post.el.remove();
                    post.el = post_render(post, that);
                    post.width = post.el.scrollWidth;
                    post.height = post.el.offsetHeight;
                    //$(that.el).css('opacity', 1.0);
                    $(post.el).css('opacity', old_opacity);
                    //$(post.el).transition({'opacity': old_opacity}, 200);

                    that.el.style.opacity = 1.0;
                    }, 1000);
            } else {
                console.log("replacing content in post:" + post.id);
                post.el.remove();
                post.el = post_render(post, that);
            }

        }

        // scroll zones set new display_time values, based on size of
        // item, and scroll speed, so don't update from server.

        if (this.type === 'fade') {
            post.display_time = newData.display_time;
        }

    },

    showPost: function (post, after_cb) {
        "use strict";
        // show this post object, fading out any current post,
        // and setting this post to be the new current post.
        var that = this;

        // if there is no current post to fade from:

        if (this.current_post === false) {
            // first post!
            this.current_post = post;
            post_fadein(this.current_post, after_cb);

            // posttype 'display' callback:
            post_display(post);

            return;
        }

        // if this post is *already* the current post:

        if (post.id === this.current_post.id) {
            // same post!
            if (this.type == 'scroll') {
                post_fadeout(post, function() { post_fadein(post, after_cb); } );
            } else {
                // leave the post up, but run the specified 'after fadein' callback
                after_cb();
            }
            return;
        }

        // if it's not return'd already, then we have a new post to fade to.

        post_fadeout(this.current_post, function () {
            // callback *after* the previous post has faded out:

            // posttype 'hide' callback:
            post_hide(that.current_post);

            // set current post, and fade it in:

            that.current_post = post;
            post_fadein(that.current_post, after_cb);

            // posttype 'display' callback:
            post_display(post);
        });

        // My work here is done.

        return;

    },

    findNextPost: function (already_gone_once) {
        "use strict";

        var thispost,
            i,
            index;

        // return a function for removing an element from the DOM.
        var make_removeel = function (post) {
            return function () {
                post && post.hasOwnProperty('el') && post.el.remove(); }; };


        // check timing restrictions, 'delete_me' tags, and otherwise, use it.

        for (index = this.current_post_index - 1, i=0;
             index !== this.current_post_index, i < this.posts.length;
             index -= 1, i++) {

            // wrap around:
            if (index < 0) {
                if (this.posts.length === 0) {
                    return undefined;
                } else {
                    index = this.posts.length - 1;
                }
            }

            thispost = this.posts[index];

            // check delete_me tags:

            if (!thispost) {
                continue;
                }

            if (thispost.hasOwnProperty('delete_me')) {
                console.log(this.name +
                            '|dropping post from feed (and removing el):' +
                            thispost.id);

                post_fadeout(thispost, make_removeel(this.posts.splice(index, 1)));

                if (this.current_post_index > index) {
                    this.current_post_index -= 1;
                }

                continue;

            }

            if (!any_relevent_restrictions(thispost)) {
                // we have a winner!
                this.current_post_index = index;
                return thispost;
            } else {
                if (this.current_post_index === index) {
                    console.log('current post has time restriction! fading out...');
                    post_fadeout(thispost);
                    this.current_post_index = -1;
                    this.current_post = false;
                }
            }

        }

        return this.current_post;

    },

    postTimeFinished: function () {
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

        var nextpost = false, that = this;

        // call this function again, used as a callback:
        var call_me_again = function () { that.postTimeFinished(); };

        // if there are no posts, then schedule to call this again later, and return:

        if (that.posts.length === 0) {
            // no posts!
            this.current_post = false;
            setTimeout(call_me_again, this.no_posts_wait);
            console.log('no posts for ' + this.name + '!');
            return;
        }

        // is there a post available for us to show?

        nextpost = this.findNextPost();

        //////////////////////////////////////////////////////////////////////////
        //
        // if a nextpost was selected, then let's display it.

        if (nextpost) {
            that.showPost(nextpost, function () {
                that.next_post_timer = setTimeout(call_me_again, nextpost.display_time);
                });
            return;
        }

        // if we've got this far, then it didn't return earlier with a next post. so...
        // no posts currently allowed!
        if (that.current_post) {
            // ok, no posts allowed, but there *is* a current post.
            // let's get rid of it.

            post_fadeout(that.current_post, function () {
                // callback once the post is faded out...

                if (!that.current_post) {
                    console.log('gone!');
                    return;
                }

                // posttype 'hide' callback:
                post_hide(post);
            });

        }

        that.current_post = false;
        that.next_post_timer = setTimeout(call_me_again, that.no_posts_wait);
        console.log('no posts currently valid in that' + that.name + '!');
        return;

    },

    pollForNewPosts: function (delay) {
        'use strict';
        // poll the server for new feeds.
        var that=this;

        safeGetJSON(this.feedsurl, function (data) {
            that.update_cb(data);
            setTimeout(function() { that.pollForNewPosts(); },
                       delay || that.update_zones_timer);
            });
    }
};

//////////////////////////////////////////////////////////////////////////////

function StreetScreen(element, initial_data) {
    "use strict";
    var i, zone,
        that = this,
        // vars for aspect ratio setting on load:
        forceaspect = window.LOCALOPTS.forceaspect,
        windowheight = $('#zones').height(),
        newheight = document.body.scrollWidth / forceaspect,
        newtop = parseInt(window.LOCALOPTS.forcetop, 10);

    // default mutable type properties:
    this.zones = [];

    // initial element:
    this.el = element;

    // set bg:
    $(element).css('background-image',
                   background_from_value(initial_data.background));

    // set screen size & aspect ratio over-rides:

    if (forceaspect !== undefined) {
        forceaspect = parseFloat(forceaspect);
        if (forceaspect) {
            $('#zones').height(newheight);
            if (isNaN(newtop)) {
                newtop = ((windowheight - newheight)/2);
            }
            $('#zones').css('top', newtop + 'px');
        }
    }

    // load values from initial data:
    this.id = initial_data.id;
    this.md5 = initial_data.md5;

    // add the zones:
    for (i = 0; i < initial_data.zones.length; i += 1) {
        zone = new Zone(this.el, initial_data.zones[i]);
        this.zones.push(zone);

        // 100 * i so that we separate our requests out,
        // in theory, we shouldn't have to handle multiple
        // in the same render frame later on.

        zone.pollForNewPosts (100 * i);
    }

    // start it all off!
    setTimeout(function () { that.update(); }, 3000);


}

StreetScreen.prototype = {
    background: "black",
    css:"",
    md5: "12345",

    update: function () {
        'use strict';
        // get JSON data from the server, check that the screen hasn't changed
        // too much, and if it has, reload.
        var this_screen = this,

            update = function (data) {
            if (data.md5 === this_screen.md5) {
                setTimeout(function () {this_screen.update();}, 50030);
            } else {
                // The md5 is different! we should do some updates!
                // TODO: proper reloading, including pre-downloading background
                //       images before displaying them, updating zone feeds, etc.
                reload_page();
            }
        };

        console.log('getting screen updates...');

        safeGetJSON('/screens/json/' +  this_screen.id + '/' + this_screen.md5,
                update, 50000);

    },

    start_zones: function () {
        'use strict';
        // go through all the zones, and start them off pulling posts
        // from the server.

        var i;

        for (i=0; i<this.zones.length; i += 1) {
            this.zones[i].postTimeFinished();
        }
    }
};

//////////////////////////////////////////////////////////////////////////////

function make_updater(zone) {
    'use strict';
    // Returns the 'update' closure, a function which is called
    //    when we get new data (posts) from the server, and adds
    //    them into a zone. Captures zone (z) within the closure,
    //    so it can be passed to the safeGetJSON(...) callback.
    var do_next_post = function () { zone.postTimeFinished(); };

    var update_post = function (thiszone, post, data) {
        safeGetJSON(data.uri, function (x) {
            thiszone.updatePost(post, x);
            });
        };

    var new_post_ids = {},
        current_post_ids = [],
        posts_to_drop = [],
        new_data, i, n, arrId;


    if (! zone.hasOwnProperty('posts')) {zone.posts = [];}

    return function (data) {


        // clear old values:

        for (i in new_post_ids) {
            if (new_post_ids.hasOwnProperty(i)){
                delete new_post_ids[i];
            }
        }
        current_post_ids.length = 0;
        posts_to_drop.length = 0;

        arrId = -1;

        // make mapping of ids to new data posts array:

        for (i=0; i < data.posts.length; i += 1) {
            new_post_ids[data.posts[i].id]=i;
        }

        // go through old posts. check if they're in need of change:

        for (i=0; i < zone.posts.length; i += 1) {

            // keep current posts, and delete no-longer needed posts:
            if (new_post_ids[zone.posts[i].id] !== undefined) {

                arrId = new_post_ids[zone.posts[i].id];

                // therefore the post IS in the new list of posts from
                // the server.  Let's keep it around then.

                current_post_ids.push(zone.posts[i].id);

                // update post with all info from server, in case stuff has changed.
                if (data.posts[arrId].changed !== zone.posts[i].changed) {
                    update_post(zone, zone.posts[i], data.posts[arrId]);
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
                    console.log(zone.name + '|adding to dropqueue:' + zone.posts[i].id);
                    posts_to_drop.push(i);
                }
            }
        }

        // remove all posts which we previously listed for removal.
        // note reverse order here, this means
        // you don't delete earlier posts before later ones,
        // which would screw up the counting.

        posts_to_drop.sort().reverse();

        for (i = 0; i < posts_to_drop.length; i += 1) {
            zone.posts.splice(posts_to_drop[i], 1);
        }

        // add new posts to the list!
        for (i=0; i<data.posts.length; i += 1) {
            new_data = data.posts[i];

            if (current_post_ids.indexOf(data.posts[i].id) === -1) {
                safeGetJSON(data.posts[i].uri, function (x) { zone.addPost(x); });
            }
        }
    }; // end of closure...
}
