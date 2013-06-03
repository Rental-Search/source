// js/routers/routes.js

var app = app || {};


var Workspace = Backbone.Router.extend({
	routes: {
		'': 							'home',
		'stats/(:metric/)': 			'stats',
		'messages/': 					'messages',
		'ads/(:id/)(:params/)': 		'ads',
		'accounts/(:params/)':			'accounts', 
	},

	initialize: function() {
		Backbone.Tastypie.csrfToken = $('input[name=csrfmiddlewaretoken]').val()
		app.layoutView = new app.LayoutView();
		$('body').append(app.layoutView.$el);
		app.layoutView.render();
		Backbone.history.start({pushState: true, root: '/pro/dashboard/'})
	},

	home: function() {
		app.layoutView.setSelectedNavTabViewAtIndex(0);
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
		app.layoutView.setSelectedNavTabViewAtIndex(2);
	},

	ads: function(id, params) {
		app.layoutView.setSelectedNavTabViewAtIndex(3);
		app.layoutView.selectedNavTabView.setDetailViewWithId(id, function() {
			if( _.isNull(params) ) {
				app.layoutView.selectedNavTabView.selectedDetailView.setSelectedNavTabViewAtIndex(0);
			} else if ( params == 'pictures' ) {
				app.layoutView.selectedNavTabView.selectedDetailView.setSelectedNavTabViewAtIndex(1);
			} else if ( params == 'prices' ) {
				app.layoutView.selectedNavTabView.selectedDetailView.setSelectedNavTabViewAtIndex(2);
			}
		});
	},
	
	accounts: function(params) {
		app.layoutView.setSelectedNavTabViewAtIndex(4);

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