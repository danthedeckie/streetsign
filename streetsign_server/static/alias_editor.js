var AliasModel = function(input_data) {
    var alias=this;
    input_data = input_data || {};

    alias.name = ko.observable(input_data.name || 'client-name...');
    alias.show_on_dashboard = ko.observable(input_data.show_on_dashboard || false);

    alias.screen_name = ko.observable(input_data.screen_name || 'Default');
    alias.screen_type = ko.observable(input_data.screen_type || 'basic');

    alias.fadetime = ko.observable(input_data.fadetime || null);
    alias.scrollspeed = ko.observable(input_data.scrollspeed || null);
    alias.forceaspect = ko.observable(input_data.forceaspect || null);
    alias.forcetop = ko.observable(input_data.forcetop || null);

    alias.url = ko.computed(function () {
        return '/client/' + this.name();
        }, alias);

};

var AliasesView = function(initial_list) {
    var view=this,
        i;

    view.aliases = ko.observableArray();
    view.screen_names = ['Default', '16:9']; // TODO
    view.view_types = ['basic', 'notrans', 'mobile'];

    for (i=0;i<initial_list.length;i++) {
        view.aliases.push(new AliasModel(initial_list[i]));
    }

    view.addAlias = function() {
        view.aliases.push(new AliasModel());
    };

    view.deleteAlias = function(alias) {
        if (confirm("Really delete this alias?")) {
            view.aliases.remove(alias);
        }
    };

    view.saveAliases = function() {
        $.post('/aliases',
            {'aliases': ko.toJSON(view.aliases)},
            function(){alert('saved!');})
         .fail(function(){alert('failed to save...');});

    };
};
