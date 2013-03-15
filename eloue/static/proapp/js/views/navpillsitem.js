// js/views/navpillsitem.js

var app = app || {};


app.NavPillsItemView = Backbone.View.extend({
	tagName: 'li',

	template: _.template($("#navpillsitem-template").html()),

	path: '',

	icon: '',

	labelName: '',

	itemName: '',

	events: {
		'click a': 'selectedItem'
	},

	initialize: function (){
		if (this.options.path) this.path = this.options.path;
		if (this.options.icon) this.icon = this.options.icon;
		if (this.options.labelName) this.labelName = this.options.labelName;
		if (this.options.itemName) this.itemName = this.options.itemName;
	},

	render: function() {
		this.$el.html(this.template({'icon': this.icon, 'label': this.labelName, 'path': this.path}));
		return this;
	},

	setUnactiveItem: function() {
		this.$el.removeClass("active");
	},

	setActiveItem: function() {
		this.$el.addClass("active");
	},

	selectedItem: function(e) {
		e.preventDefault();
		app.appRouter.navigate(this.path, {trigger: true});
	}
});