// js/views/layout.js

var app = app || {};

app.LayoutView = Backbone.View.extend({
	id: 'pro-app',

	className: 'container-fluid',

	navPillsView: new app.NavPillsView(),

	initialize: function() {
		this.navPillsView.pushNavPillItemView(new app.NavPillsItemView({icon: "home", labelName: "Acceuil"}));
		this.navPillsView.pushNavPillItemView(new app.NavPillsItemView({icon: "stats", labelName: "Statistique", path: "stats/"}));
		this.navPillsView.pushNavPillItemView(new app.NavPillsItemView({icon: "envelope", labelName: "Messages", path: "messages/"}));
		this.navPillsView.pushNavPillItemView(new app.NavPillsItemView({icon: "show_thumbnails_with_lines", labelName: "Annonces", path: "ads/"}));
		this.navPillsView.pushNavPillItemView(new app.NavPillsItemView({icon: "nameplate", labelName: "Paramètres", path: "settings/"}));
	},

	render: function() {
		this.$el.prepend(this.navPillsView.$el);
		this.navPillsView.render();
		return this;
	},

	renderNavPillContent: function(view) {
		this.$el.append(view.$el);
		view.render();
	}
});