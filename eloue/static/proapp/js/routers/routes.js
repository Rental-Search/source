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
});