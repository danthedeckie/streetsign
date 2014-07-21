var AliasModel = function(input_data) {
    var alias=this;
    alias.name = ko.observable();
    alias.screen_name = ko.observable('Default');
    alias.screen_type = ko.observable('basic');
    alias.fadetime = ko.observable(null);
    alias.scrollspeed = ko.observable(null);
    alias.forceaspect = ko.observable(null);
    alias.forcetop = ko.observable(null);
};

var AliasesView = function(initial_list) {
    var view=this,
        i;

    view.aliases = ko.observableArray();
    view.screen_names = ['Default', '16:9']; // TODO

    for (i=0;i<initial_list.length;i++) {
        view.aliases.push(new AliasModel(initial_list[i]));
    }

    view.addAlias = function() {
        view.aliases.push(new AliasModel());
    };

    view.deleteAlias = function(alias) {
        view.aliases.remove(alias);
    };
};
