// js/views/core/nav.js

var app = app || {};

app.NavView = Backbone.View.extend({
	navTabsViews: [],

	selectedNavTabView: null,

	initialize: function() {

	},

	setNavTabsView: function(navTabs) {
		this.navTabsViews = navTabs;
		this.trigger('navtabs:change');
	},

	setSelectedNavTabView: function(tab) {
		this.selectedNavTabView = tab;
		this.trigger('selectednavtab:change');
	}

	render: function() {},

	renderNavTabsItems: function() {},

	renderNavTabView: function() {},
});