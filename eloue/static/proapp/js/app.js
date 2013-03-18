// js/app.js

var app = app || {};


$(function() {
	console.log("---- App starting ----");
	app.appRouter = new Workspace();
	Backbone.history.start({pushState: true, root: '/pro/dashboard/'})
	$('body').append(app.layoutView.$el);
	app.layoutView.render();
	console.log("---- App started ----");
});