// js/app.js

var app = app || {};


$(function() {
	console.log("---- App starting ----");
	app.appRouter = new Workspace();
	
	app.layoutView = new app.LayoutView();
	$('body').append(app.layoutView.el);

	Backbone.history.start({pushState: true, root: '/pro/dashboard/'})
	console.log("---- App started ----");
});