// js/routers/routes.js

var app = app || {};


var Workspace = Backbone.Router.extend({
	routes: {
		'': 						'home',
		'stats/(:metric/)': 		'stats',
		'messages/': 				'messages',
		'ads/(:id/)': 					'ads',
		'accounts/(:params/)':		'accounts', 
	},

	initialize: function() {
		Backbone.Tastypie.csrfToken = $('input[name=csrfmiddlewaretoken]').val()
		app.layoutView = new app.LayoutView();
		$('body').append(app.layoutView.$el);
		app.layoutView.render();
		Backbone.history.start({pushState: true, root: '/pro/dashboard/'})
	},

	home: function() {
		if ( app.layoutView.selectedNavTabView instanceof app.layoutView.navTabViews[0] ) {
		} else {
			app.layoutView.setSelectedNavTabViewAtIndex(0);
		}
	},

	stats: function(metric) {
		app.layoutView.setSelectedNavTabViewAtIndex(1);
		
		if( _.isNull(metric) ) {
			app.layoutView.selectedNavTabView.setSelectedNavTabViewAtIndex(0);
		} else if (metric == 'redirection') {
			app.layoutView.selectedNavTabView.setSelectedNavTabViewAtIndex(1);
		} else if (metric == 'phone') {
			app.layoutView.selectedNavTabView.setSelectedNavTabViewAtIndex(2);
		} else if (metric == 'address') {
			app.layoutView.selectedNavTabView.setSelectedNavTabViewAtIndex(3);
		}
	},
	messages: function() {
		if ( app.layoutView.selectedNavTabView instanceof app.layoutView.navTabViews[2] ) {
		} else {
			app.layoutView.setSelectedNavTabViewAtIndex(2);
		}
	},

	ads: function(id) {
		if ( app.layoutView.selectedNavTabView instanceof app.layoutView.navTabViews[3] ) {
		} else {
			app.layoutView.setSelectedNavTabViewAtIndex(3);
		}

		if( !_.isNull(id) ) {
			app.layoutView.selectedNavTabView.setDetailViewWithId(id);
		}

	},
	
	accounts: function(params) {
		if ( app.layoutView.selectedNavTabView instanceof app.layoutView.navTabViews[4] ) {
		} else {
			app.layoutView.setSelectedNavTabViewAtIndex(4);
		}

		if( _.isNull(params) ) {
			app.layoutView.selectedNavTabView.setSelectedNavTabViewAtIndex(0);
		} else if (params == 'shop') {
			app.layoutView.selectedNavTabView.setSelectedNavTabViewAtIndex(1);	
		} else if (params == 'billing') {
			app.layoutView.selectedNavTabView.setSelectedNavTabViewAtIndex(2);	
		} else if (params == 'plan') {
			app.layoutView.selectedNavTabView.setSelectedNavTabViewAtIndex(3);	
		}
	}
});