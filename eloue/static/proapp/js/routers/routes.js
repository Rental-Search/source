// js/routers/routes.js

var app = app || {};


var Workspace = Backbone.Router.extend({
	routes: {
		'': 					'home',
		'stats/': 				'stats',
		'messages/': 			'messages',
		'ads/': 				'ads',
		'accounts/':			'accounts', 
	},

	initialize: function() {
		Backbone.Tastypie.csrfToken = $('input[name=csrfmiddlewaretoken]').val()
		app.layoutView = new app.LayoutView();
		$('body').append(app.layoutView.$el);
		app.layoutView.render();

		Backbone.history.start({pushState: true, root: '/pro/dashboard/'})
	},

	home: function() {
		app.layoutView.setSelectedNavTabViewAtIndex(0)
	},
	stats: function() {
		app.layoutView.setSelectedNavTabViewAtIndex(1)
	},
	messages: function() {
		app.layoutView.setSelectedNavTabViewAtIndex(2)
	},
	ads: function() {
		app.layoutView.setSelectedNavTabViewAtIndex(3)
	},
	accounts: function() {
		app.layoutView.setSelectedNavTabViewAtIndex(4)
	}
});