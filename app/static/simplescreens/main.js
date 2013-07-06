function url_insert(url, data) {
    return url.replace(/-1/, data);
}

window.zones = [];

function zone_html(id, top, left, bottom, right) {
    return ('<div id="_zone_'+id+'" class="zone" style="'
            +'left:' + left
            +';right:' + right
            +';bottom:' + bottom
            +';top:' + top + '">'+id+'</div>');
    return x;
}

function zone(container, obj) {
    window.zones.push(obj);

    obj.el = $(zone_html(obj.name, obj.top, obj.left, obj.bottom, obj.right))
              .prependTo(container)[0];

    obj.el.innerHTML = obj.el.innerHTML + '<br/>(initialising)';
}

function update_zones_posts() {
    for (var i in window.zones) {
        var zone = window.zones[i];
        function update(data){ zone.el.innerHTML = data; }

        $.get(url_insert(POSTS_URL, JSON.stringify(zone.feeds)), update);
        //window.zones[z].el.innerHTML = 'updated';
    }
    // TODO: get this value from somewhere:
    setTimeout(update_zones_posts, 32000);
}
