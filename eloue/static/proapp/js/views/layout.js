// js/views/layout.js

var app = app || {};

app.LayoutView = app.NavView.extend({
	id: 'pro-app',

	className: 'container-fluid',

	initialize: function() {
		//Extend the class name for navpills
		this.navTabItemsView = this.navTabItemsView.extend({className:  'nav nav-pills  top-nav'});
		
		this.navTabViews = [app.StatsPillContentView];
	},
});