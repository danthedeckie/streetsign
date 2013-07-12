function make_time_observable(t){
    return { start: ko.observable (t['start']),
               end: ko.observable (t['end']),
              note: ko.observable (t['note']) }
}

var TimesModel = function(times) {
    var self = this;

    self.times = ko.observableArray(times.map(make_time_observable));

    self.addTime = function() {
        self.times.push({
            start: ko.observable("00:20"),
            end: ko.observable("23:30"),
            note: ko.observable("")
        });
    };
    self.removeTime = function(t) {
        self.times.remove(t);
    };
};


