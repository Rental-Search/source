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
		app.layoutView.setCurrentNavPillContent(homeNavPillContentView);
		app.layoutView.renderNavPillContent();
	},

	stats: function() {
		app.layoutView.navPillsView.navPillsItemViews[1].setSelectedPillItem();
		var statsNavPillContentView = new app.StatsNavPillContentView();
		app.layoutView.setCurrentNavPillContent(statsNavPillContentView);
		app.layoutView.renderNavPillContent();
	},

	messages: function() {
		app.layoutView.navPillsView.navPillsItemViews[2].setSelectedPillItem();
		var messagesNavPillContentView = new app.NavPillContentView();
		messagesNavPillContentView.id = 'messages';
		app.layoutView.setCurrentNavPillContent(messagesNavPillContentView);
		app.layoutView.renderNavPillContent();
	},

	ads: function() {
		app.layoutView.navPillsView.navPillsItemViews[3].setSelectedPillItem();
		var adsNavPillContentView = new app.NavPillContentView();
		adsNavPillContentView.id = 'ads';
		app.layoutView.setCurrentNavPillContent(adsNavPillContentView);
		app.layoutView.renderNavPillContent();
	},

	settings: function() {
		app.layoutView.navPillsView.navPillsItemViews[4].setSelectedPillItem();
		var settingsNavPillContentView = new app.NavPillContentView();
		settingsNavPillContentView.id = 'settings';
		app.layoutView.setCurrentNavPillContent(settingsNavPillContentView);
		app.layoutView.renderNavPillContent();
	}
});