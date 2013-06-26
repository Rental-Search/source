// js/routers/routes.js

var app = app || {};


var Workspace = Backbone.Router.extend({
	routes: {
		'stats/(:metric/)': 			'stats',
	},

	initialize: function() {
		Backbone.Tastypie.csrfToken = $('input[name=csrfmiddlewaretoken]').val()
		app.layoutView = new app.LayoutView();
		$('body').append(app.layoutView.$el);
		app.layoutView.render();
		Backbone.history.start({pushState: true, root: '/pro/dashboard/'})
	},

	stats: function(metric) {
		app.layoutView.setSelectedNavTabViewAtIndex(0);
		
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
});