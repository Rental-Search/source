// js/app.js

var app = app || {};


$(function() {
	console.log("---- App starting ----");
	app.appRouter = new Workspace();
	new app.LayoutView();
	Backbone.history.start({pushState: true, root: '/pro/dashboard/'})
	console.log("---- App started ----");
});