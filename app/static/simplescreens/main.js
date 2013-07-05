window.zones = [];

function zone_html(id, top, left, bottom, right) {
    var x = ('<div id="'+id+'" class="zone" style="'
            +'   left:' + left
            +' ;right:' + right
            +';bottom:' + bottom
            +'   ;top:' + top + '"></div>');
    alert (x);
    return x;
}


function zone(container, obj) {
    window.zones.push(obj);

    obj.el = $(container).prepend(zone_html(
                obj.id, obj.top, obj.left, obj.bottom, obj.right)).fadeIn();

}
