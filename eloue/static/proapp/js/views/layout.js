// js/views/layout.js

var app = app || {};

app.LayoutView = Backbone.View.extend({
	id: 'pro-app',

	className: 'container-fluid',

	initialize: function() {
		this.navPillsView = new app.NavPillsView();
		this.navPillsView.on('navpillcontentselected:change', this.renderContentPill, this)
		this.render();
	},

	render: function() {
		this.renderNavPill();
		//this.renderContentPill();
		this.$el.appendTo("body");
		return this;
	},

	renderNavPill: function() {
		this.$el.append(this.navPillsView.render().el);
	},

	renderContentPill: function() {
		if (this.$el.children(".content-pill").length) this.$el.children(".content-pill").remove();
		this.$el.append(this.navPillsView.selectedPillContentView.render().el);
	},
});