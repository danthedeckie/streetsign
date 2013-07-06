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
    for (var z in window.zones) {
        $.get(
        window.zones[z].el.innerHTML = 'updated';
    }
    setTimeout(update_zones_posts, 12000);
}
