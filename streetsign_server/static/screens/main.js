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
    'use strict';
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

    var csspairs = cssPairs(initial_data.css), i, that = this;

    var update = function (name) {
        if (initial_data.hasOwnProperty(name)) {
            that[name] = initial_data[name];
        }
        };

    // default "mutable type" properties:
    this.posts = [];
    this.feeds = [];


    // update zone from initial data.
    // this could probably be done better by some ECMA5 function?
    // or even $.extend...
    update('feeds');
    update('color');
    update('name');
    update('type');
    update('fadetime');

    console.log(this.type);

    this.el = $(zone_html(initial_data.name,
                          initial_data.top,
                          initial_data.left,
                          initial_data.bottom,
                          initial_data.right,
                          initial_data.css,
                          initial_data.type)).prependTo(container)[0];

    for (i = 0; i < csspairs.length; i += 1) {
        this.el.style[csspairs[i][0]] = csspairs[i][1];
        //$(this.el).css(csspairs[i][0], csspairs[i][1]);
    }

}

Zone.prototype = {
    // default "immutable type" properties:
    type: 'fade',
    color: 'white',
    post_time: 4000,
    fadetime: 500,
    update_zones_timer: 6000,
    no_posts_wait: 10000,
    current_post: false,

    // methods:
    addPost: function (index) {
        "use strict";
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

        // Maybe better not ?
        if (JSON.stringify(post.content) !== JSON.stringify(newData.content)) {

            post.content = newData.content;

            if (this.current_post.id === post.id) {
                that.el.style.opacity = 0;
                //$(that.el).css('opacity', 0);
                setTimeout( function () {
                    console.log("replacing content in live post");
                    post.el.remove();
                    post.el = post_types[post.type].render(that.el, post)[0];
                    //$(that.el).css('opacity', 1.0);
                    that.el.style.opacity = 1.0;
                    }, 1000);
            } else {
                console.log("replacing content in post:" + post.id);
                post.el.remove();
                post.el = post_types[post.type].render(this.el, post)[0];
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
            post_fadein(this.current_post, this.fadetime, after_cb);

            // posttype 'display' callback:
            if (post_types[post.type].hasOwnProperty('display')) {
                post_types[post.type].display(post);
            }

            return;

        }

        // if this post is *already* the current post:

        if (post.id === this.current_post.id) {
            // same post!
            console.log('only this post is available');

            if (this.type == 'scroll') {
                post_fadein(post, this.fadetime, after_cb);
            } else {
                after_cb();
            }
            return;
        }

        // if it's not return'd already, then we have a new post to fade to.

        post_fadeout(this.current_post, this.fadetime, function () {
            // callback *after* the previous post has faded out:

            // posttype 'hide' callback:
            if (post_types[that.current_post.type].hasOwnProperty('hide')) {
                post_types[that.current_post.type].hide(that.current_post);
            }

            // set current post, and fade it in:

            that.current_post = post;
            post_fadein(that.current_post, that.fadetime, after_cb);

            // posttype 'display' callback:
            if (post_types[post.type].hasOwnProperty('display')) {
                post_types[post.type].display(post);
            }

        });

        // My work here is done.

        return;

    },

    findNextPost: function () {
        "use strict";
        // go through all the posts in this feed, move any which are
        // disallowed by time restrictions to the end of the list, and
        // return the next post to display, if there is one, else undefined.

        var appendlist = [], thispost, nextpost;

        // return a function for removing an element from the DOM.
        var make_removeel = function (post) {
            return function () {
                post.el.remove(); }; };

        while (this.posts.length > 0) {

            thispost = this.posts.shift();

            // if it's sheduled for deletion, DON'T add it to the new list,
            // but fade it out (if it is visible) and delete the element.

            if (thispost.hasOwnProperty('delete_me')) {
                post_fadeout(thispost, this.fadetime, make_removeel(thispost));

                console.log(this.name +
                            '|dropping post from feed (and removing el):' +
                            thispost.id);
                continue;
            }

            // fine, it's not scheduled for deletion, so stuff it on the
            // appendlist stack:

            appendlist.push(thispost);

            // check time restrictions.  If they allow this post to be shown,
            // then we'll use it as the next one to display!

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

        // add delayed posts (including new 'thispost') on to the end of
        // the queue.

        this.posts = this.posts.concat(appendlist);

        return thispost;

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
            that.current_post = false;
            setTimeout(call_me_again, that.no_posts_wait);
            console.log('no posts for ' + that.name + '!');
            return;
        }

        // go through all the current posts, move any which aren't tagged for deletion
        // onto a new "appendlist". shunt any posts which are time restricted to the end
        // of the list, so they won't get shown now, but stay in the list.

        nextpost = that.findNextPost();

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

            post_fadeout(that.current_post, that.fadetime, function () {
                // callback once the post is faded out...

                if (!that.current_post) {
                    console.log('gone!');
                    return;
                }

                // posttype 'hide' callback:
                if (post_types[that.current_post.type].hasOwnProperty('hide')) {
                    post_types[that.current_post.type].hide(that.current_post);
                }

            });

        }

        that.current_post = false;
        that.next_post_timer = setTimeout(call_me_again, that.no_posts_wait);
        console.log('no posts currently valid in that' + that.name + '!');
        return;


    },

    pollForNewPosts: function () {
        'use strict';
        // poll the server for new feeds.
        var that=this;

        getJSON(url_insert(POSTS_URL, JSON.stringify(this.feeds)),
                  make_updater(this));


        // schedule myself to un again later...
        setTimeout(function () { that.pollForNewPosts(); },
                   this.update_zones_timer);
    }
};


function getJSON(url, callback) {
    var xhr = new XMLHttpRequest();
    if (callback) {
    xhr.onreadystatechange = function() {
      if (xhr.readyState == 4) {
         callback(JSON.parse(xhr.responseText));
      }
    }
    }
    xhr.open("GET", url, true);
    xhr.send(null);

}

//////////////////////////////////////////////////////////////////////////////

function StreetScreen(element, initial_data) {
    "use strict";
    var i, that = this;

    // default mutable type properties:
    this.zones = [];

    // initial element:
    this.el = element;

    // set bg:
    $(element).css('background-image',
                   background_from_value(initial_data.background));

    // load values from initial data:
    this.id = initial_data.id;
    this.md5 = initial_data.md5;

    // add the zones:
    for (i = 0; i < initial_data.zones.length; i += 1) {
        this.zones.push(new Zone(this.el, initial_data.zones[i]));
        this.zones[i].pollForNewPosts();
    }

    // start it all off!
    //update_zones_posts();
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
        var that = this;

        console.log('getting screen updates...');

        var update = function (data) {
            if (data.md5 === that.md5) {
                setTimeout(function () {that.update();}, 50000);
            } else {
                // The md5 is different! we should do some updates!
                // TODO: proper reloading, including pre-downloading background
                //       images before displaying them, updating zone feeds, etc.
                reload_page();
            }
        };

        getJSON('/screens/json/' +  that.id + '/' + that.md5, update);

        // And for now, since there isn't really anywhere better, lets also
        // tell all external sources to update if they need to.
        getJSON('/external_data_sources/');
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

function make_updater(z) {
    'use strict';
    // Returns the 'update' closure, a function which is called
    //    when we get new data (posts) from the server, and adds
    //    them into a zone. Captures zone (z) within the closure,
    //    so it can be passed to the $.getJSON(...) callback.
    var zone = z;
    var do_next_post = function () { zone.postTimeFinished(); };
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
                zone.updatePost(zone.posts[i], data.posts[arrId]);
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

        for (i = 0; i < posts_to_drop.length; i += 1) {
            zone.posts.splice(posts_to_drop[i], 1);
        }

        // add new posts to the list!
        for (i=0; i<data.posts.length; i += 1) {
            new_data = data.posts[i];

            if (current_post_ids.indexOf(new_data.id) === -1) {
                // add the new post to zone.posts, and get the array index:
                new_data.zone = zone;
                new_data.el =
                    post_types[new_data.type].render(zone.el, new_data)[0];
                new_data.el.style.transition = "opacity 0." + zone.fadetime + "s";
                new_data.el.style.webkitTransition = "opacity 0." + zone.fadetime + "s";
                new_data.el.style.display = "none";
                //$(new_data.el).css('opacity',0);
                //new_data.el.style.opacity = 0;

                zone.posts.push(new_data);

            }
        }
    }; // end of closure...
}
