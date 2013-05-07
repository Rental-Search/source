// js/views/core/navtabs.js

var app = app || {};

app.NavTabsView = Backbone.View.extend({
	tagName: 'ul',

	navTabsItemsViews: [],


	initialize: function() {

	},

	setNavTabsItemsViews: function(navTabsItems) {
		this.navTabsItemsViews = [];
		this.trigger('navtabs: change');
	},

	render: function() {},

	renderItem: function() {},
});