// js/routers/routes.js

var app = app || {}


var Workspace = Backbone.Router.extend({
	routes: {
		'': 					'home',
		'stats/': 				'stats',
		'stats/:metric/': 		'stats',
		'messages/': 			'messages',
		'ads/': 				'ads',
		'accounts/':			'accounts',
		'accounts/:metric/':	'accounts',
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

	stats: function(metric) {
		app.layoutView.navPillsView.navPillsItemViews[1].setSelectedPillItem();
		
		if (app.layoutView.currentNavPillContent instanceof app.StatsNavPillContentView) {
			var statsNavPillContentView = app.layoutView.currentNavPillContent;
		} else {
			var statsNavPillContentView = new app.StatsNavPillContentView();
			app.layoutView.setCurrentNavPillContent(statsNavPillContentView);
			app.layoutView.renderNavPillContent();
		}

		if ( _.isUndefined(metric) ) {
			var navTabContentView = new app.TrafficNavTabContentView({titleName: 'Visites'});
			statsNavPillContentView.navTabsView.navTabsItemViews[0].setSelectedTabItem();
		} else if (metric == 'redirection') {
			var navTabContentView = new app.RedirectionNavTabContentView({titleName: 'Redirections'});
			statsNavPillContentView.navTabsView.navTabsItemViews[2].setSelectedTabItem();
		} else if (metric == 'phone') {
			var navTabContentView = new app.PhoneNavTabContentView({titleName: 'Appels'});
			statsNavPillContentView.navTabsView.navTabsItemViews[1].setSelectedTabItem();
		} else if (metric == 'address') {
			var navTabContentView = new app.AddressNavTabContentView({titleName: 'Adresses'});
			statsNavPillContentView.navTabsView.navTabsItemViews[3].setSelectedTabItem();
		}

		statsNavPillContentView.setCurrentNavTabContentView(navTabContentView);
		statsNavPillContentView.renderNavTabContent();
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

	accounts: function(metric) {
		app.layoutView.navPillsView.navPillsItemViews[4].setSelectedPillItem();

		if (app.layoutView.currentNavPillContent instanceof app.AccountsNavPillContentView) {
			var accountsNavPillContentView = app.layoutView.currentNavPillContent;
		} else {
			var accountsNavPillContentView = new app.AccountsNavPillContentView();
			app.layoutView.setCurrentNavPillContent(accountsNavPillContentView);
			app.layoutView.renderNavPillContent();
		}

		if( _.isUndefined(metric) ) {
			var navTabContentView = new app.PatronNavTabContentView({titleName: 'Informations sur la gérant'});
			accountsNavPillContentView.navTabsView.navTabsItemViews[0].setSelectedTabItem();
		} else if ( metric == 'shop' ) {
			var navTabContentView = new app.ShopNavTabContentView({titleName: 'Informations sur l\'agence'});
			accountsNavPillContentView.navTabsView.navTabsItemViews[1].setSelectedTabItem();
		} else if ( metric == 'billing' ) {
			var navTabContentView = new app.BillingNavTabContentView({titleName: 'Facturation'});
			accountsNavPillContentView.navTabsView.navTabsItemViews[2].setSelectedTabItem();
		} else if ( metric == 'plan' ) {
			var navTabContentView = new app.PlanNavTabContentView({titleName: 'Abonnements'});
			accountsNavPillContentView.navTabsView.navTabsItemViews[3].setSelectedTabItem();	
		}

		accountsNavPillContentView.setCurrentNavTabContentView(navTabContentView);
		accountsNavPillContentView.renderNavTabContent();
	}
});