function any_time_options(newstuff) {
    return ( $.extend( {},
        { askEra: false,
          askSecond: false,
          earliest: new Date(),
          //format: "%a - %e/%M/%y - %k:%i"
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

$('input[type=number]').blur( function (e) {
    // 'fix' crap lack of type=number support in FF.
    var newnum = 1 * $(this).val();
    var min = (1 * $(this).data('min'));
    var max = (1 * $(this).data('max'));

    if (""+newnum == "NaN")
        newnum = 0

    // could be done with max(min) whatever, but this is actually clearer:
    if (newnum < min)
        newnum = min;
    else if (newnum > max)
        newnum = max;

    $(this).val(newnum);
});

/* TODO: link this in sometime...
$('input[type=time]').blur( function (e) {
    var newtime = $(this).val();
    
    var HHMM = /\d{1,2}:\d{1,2}/;

    var output = newtime.match(HHMM);

    if (output == null)
        $(this).val('00:00');
        return true;

    if (output.length == 3) {
        hours = Math.max(0, Math.min(23, output[1]));
        mins = Math.max(0, Math.min(59, output[2]));
    }

    $(this).val(hours + ':' + mins);
}); */

/***************************************************************/

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


