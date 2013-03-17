// js/views/layout.js

var app = app || {};

app.LayoutView = Backbone.View.extend({
	id: 'pro-app',

	className: 'container-fluid',

	initialize: function() {
		this.navPillsView = new app.NavPillsView();
		this.navPillsView.on('navpillcontentselected:change', this.renderContentPill, this);
		this.render();
	},

	render: function() {
		this.$el.append(this.navPillsView.render().el);
		return this;
	},

	renderContentPill: function() {
		this.$el.children(".content-pill").hide();
		this.$el.append(this.navPillsView.selectedPillContentView.$el.show());
		this.navPillsView.selectedPillContentView.render()
	}
});