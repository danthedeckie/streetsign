var TimesModel = function(times) {
    var self = this;
    self.times = ko.observableArray(times);

    self.addTime = function() {
        self.times.push({
            start: "00:20",
            end: "23:30",
            note: ""
        });
    };
    self.removeTime = function(t) {
        self.times.remove(t);
    };
};

var viewTimesModel = new TimesModel([
    { start: "00:00", end: "23:00", note: "example"}
]);

ko.applyBindings(viewTimesModel);
