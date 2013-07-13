function any_time_options(newstuff) {
    return ( $.extend( {},
        { askEra: false,
          askSecond: false,
          earliest: new Date(),
        },
        newstuff ));
};

$('#active_start').AnyTime_picker(
    any_time_options({ lableTitle: 'Start' })
).change(function(e) {
    $('#active_end')
        .AnyTime_noPicker()
        .AnyTime_picker(any_time_options({
            earliest: $('#active_start').val(),
            labelTitle: 'End'})
        );
});
$('#active_end').AnyTime_picker(
    any_time_options({ labelTitle: 'End' }));

function make_time_observable(t){
    // turns a simple time dict into an observable one.
    return { start: ko.observable (t['start']),
               end: ko.observable (t['end']),
              note: ko.observable (t['note']) }
}

/**********************************************************/

ko.bindingHandlers.timeHandler = {
    init: function(element, valueAccessor) {
        $(element).val(valueAccessor()());
        $(element).timePicker();
        $(element).change(function(e){
            valueAccessor()($(element).val());
            //alert('oh');
            });
    },
    update: function(element, valueAccessor) {
        $(element).val(valueAccessor()());
        }
};

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


