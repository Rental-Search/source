// js/routers/routes.js

var app = app || {}


var Workspace = Backbone.Router.extend({
	routes: {
		'': 				'home',
		'stats/': 			'stats',
		'messages/': 		'messages',
		'ads/': 			'ads',
		'settings/':		'settings',
	},

	initialize: function() {
		app.layoutView = new app.LayoutView();
	},

	home: function() {
		app.layoutView.navPillsView.navPillsItemViews[0].setSelectedPillItem();
		var homeNavPillContentView = new app.NavPillContentView();
		homeNavPillContentView.id = 'accueil';
		app.layoutView.renderNavPillContent(homeNavPillContentView);
	},
	stats: function() {
		app.layoutView.navPillsView.navPillsItemViews[1].setSelectedPillItem();
	},
	messages: function() {
		app.layoutView.navPillsView.navPillsItemViews[2].setSelectedPillItem();
	},
	ads: function() {
		app.layoutView.navPillsView.navPillsItemViews[3].setSelectedPillItem();
	},
	settings: function() {
		app.layoutView.navPillsView.navPillsItemViews[4].setSelectedPillItem();
	}
});