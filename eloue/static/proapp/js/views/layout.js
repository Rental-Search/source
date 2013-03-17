// js/views/layout.js

var app = app || {};

app.LayoutView = Backbone.View.extend({
	id: 'pro-app',

	className: 'container-fluid',

	initialize: function() {
		this.navPillsView = new app.NavPillsView();

		var homeNavPillContentView = new app.NavPillContentView();
		homeNavPillContentView.id = 'home';
		homeNavPillContentView.navPillsItemView = new app.NavPillsItemView({icon: "home", labelName: "Acceuil"});
		this.navPillsView.pushNavPillContentViews(homeNavPillContentView);

		var statsNavPillContentView = new app.StatsNavPillContentView();
		statsNavPillContentView.id = 'stats';
		statsNavPillContentView.navPillsItemView = new app.NavPillsItemView({icon: "stats", labelName: "Statistique", path: "stats/"});
		this.navPillsView.pushNavPillContentViews(statsNavPillContentView);

		var messagesNavPillContentView = new app.NavPillContentView();
		messagesNavPillContentView.id = 'messages';
		messagesNavPillContentView.navPillsItemView = new app.NavPillsItemView({icon: "envelope", labelName: "Messages", path: "messages/"});
		this.navPillsView.pushNavPillContentViews(messagesNavPillContentView);

		var adsNavPillContentView = new app.NavPillContentView();
		adsNavPillContentView.id = 'ads';
		adsNavPillContentView.navPillsItemView = new app.NavPillsItemView({icon: "show_thumbnails_with_lines", labelName: "Annonces", path: "ads/"});
		this.navPillsView.pushNavPillContentViews(adsNavPillContentView);

		var settingsNavPillContentView = new app.NavPillContentView();
		settingsNavPillContentView.id = 'settings';
		settingsNavPillContentView.navPillsItemView = new app.NavPillsItemView({icon: "nameplate", labelName: "Paramètres", path: "settings/"});
		this.navPillsView.pushNavPillContentViews(settingsNavPillContentView);



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