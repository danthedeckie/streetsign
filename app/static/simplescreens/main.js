// TODO: get these from somewhere?
NO_POSTS_WAIT = 10000; // if no posts, how long to wait?
UPDATE_ZONES_TIMER = 32000; // how often to check for new posts?
DEFAULT_POST_TIME = 5000; // default of length for a post to be visible

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
            +';top:' + top + '">'+id+'</div>');
    return x;
}

function zone(container, obj) {
    // adds an object into the window zones list,
    // and gives it an element within the container for filling with stuff.

    window.zones.push(obj);
    console.log('added one. now at:' + window.zones.length);
    obj.el = $(zone_html(obj.name, obj.top, obj.left, obj.bottom, obj.right))
              .prependTo(container)[0];

    obj.el.innerHTML = obj.el.innerHTML + '<br/>(initialising)';
}

function next_post(zone) {
    // if it's not already scrolling, start!
    if (!('current_post' in zone))
        zone.current_post = -1;

    // increment
    zone.current_post++;
    if ((!('posts' in zone)) || (zone.posts.length == 0)) {
        // there are no posts! I guess we'll sit around and wait for some.
        setTimeout(function(){next_post(zone);}, NO_POSTS_WAIT);
        console.log('no posts!');
        return;
        }

    // wrap around.
    if (zone.posts.length <= zone.current_post) {
        zone.current_post = 0;
    }

    zone.el.innerHTML = zone.posts[zone.current_post].content.content;
    //zone.el.innerHTML = 'postid:' + zone.current_post;
    console.log(zone.current_post);

    setTimeout(function(){next_post(zone);}, DEFAULT_POST_TIME);
}

function start_zones_scrolling() {
    for (var i=0;i<window.zones.length;i++) {
        console.log('start:' + i);
        next_post(window.zones[i]);
    }
}


function make_updater(z){
    // Captures zone (z) within a closure, for passing to a callback.
    var zone = z;
    return function(data) {
        zone.el.innerHTML = data.posts.length;
        zone.posts = data.posts;
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
