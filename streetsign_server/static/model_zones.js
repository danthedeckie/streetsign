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
    Screen Zones Editor knockoutjs model stuff.

*************************************************************/

DEFAULT_ZONE = { name: "zone",
                 top: "30%",
                 left: "30%",
                 right: "30%",
                 bottom: "30%",
                 type: 'fade',
                 color: '#fff',
                 fadetime: 250,
                 feeds: [],
                 css: '',
                 classes: '' };


var ScreenModel = function(background, other_settings, css, zones, color, type) {
    var self = this;

    self.other_settings = ko.observable(other_settings);
    self.background = ko.observable(background);
    self.css = ko.observable(css);
    self.color = ko.observable(color);
    self.type = ko.observable(type);
    self.zones = ko.observableArray();
    ko.mapping.fromJS(zones.map( function(x){
        return $.extend({}, DEFAULT_ZONE,x);
        }) , [], self.zones);


    // stupid knockout treats <select> options as strings.
    // the data comes in as ints.  so fake it.
    for (var zone in self.zones()){
        self.zones()[zone].feeds(
            self.zones()[zone].feeds().map(function(x){return ""+x}));
        if (! 'css' in self.zones()[zone]) {
            self.zones()[zone].css = ko.observable('');
            }
        //self.zones()[zone].css = JSON.stringify(self.zones().css);
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
