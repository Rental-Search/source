// js/app.js

var app = app || {};


$(function() {
	console.log("---- App started ----");
	Backbone.Layout.configure({ });
	new app.LayoutView();
});