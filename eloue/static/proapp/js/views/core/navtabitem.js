// js/views/core/navtabitem.js

var app = app || {};

app.NavTabItemView = Backbone.View.extend({
	tagName: 'li',

	template: null,

	path: null,

	icon: null,

	labelName: null,

	events: {
		'click a': 'selectedTabItem'
	},

	//Display the item
	render: function() {
		this.$el.html(this.template({'icon': this.icon, 'label': this.labelName, 'path': this.path}));
		return this;
	},

	//Delete css active class on the previous selected item
	unactive: function() {
		this.$el.removeClass("active");
	},

	//Add css active class on the clicked item
	active: function() {
		this.$el.addClass("active");
	},

	//Unactive the previous selected item and active the clicked item
	selectedTabItem: function(e) {
		e.preventDefault();
		app.appRouter.navigate(this.path, {trigger: true});
	}
});