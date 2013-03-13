// js/views/layout.js

var app = app || {};

app.LayoutView = Backbone.View.extend({
	id: 'pro-app',

	className: 'container-fluid',

	initialize: function() {
		this.render();
	},

	render: function() {
		this.$el.appendTo("body");
		return this;
	}
});