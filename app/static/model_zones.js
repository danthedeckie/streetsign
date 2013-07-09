DEFAULT_ZONE = { name: "zone",
                 top: "30%",
                 left: "30%",
                 right: "30%",
                 bottom: "30%",
                 feeds: [],
                 css: '',
                 classes: '' };


var ScreenModel = function(background, other_settings, css, zones) {
    var self = this;

    self.other_settings = ko.observable(other_settings);
    self.background = ko.observable(background);
    self.css = ko.observable(css);
    self.zones = ko.observableArray();
    ko.mapping.fromJS(zones, [], self.zones);


    // stupid knockout treats <select> options as strings.
    // the data comes in as ints.  so fake it.
    for (var zone in self.zones()){
        self.zones()[zone].feeds(
            self.zones()[zone].feeds().map(function(x){return ""+x}));
        self.zones()[zone].css = JSON.stringify(self.zones().css);
    }

    self.addZone = function() {
        var new_obj = {};
        $.extend(new_obj, DEFAULT_ZONE, {'name':'zone'+(self.zones().length+1)});
        self.zones.push(ko.mapping.fromJS(new_obj));
    };
    self.removeZone = function(t) {
        self.zones.remove(t);
    };

};
