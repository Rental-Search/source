// js/views/navpills.js

var app = app || {};


app.NavPillsView = Backbone.View.extend({
	tagName: 'ul',
	className: 'nav nav-pills  top-nav',

	navPillContentViews: [],

	selectedPillContentView: '',

	root: '/pro/dashboard/',


	initialize: function() {
		var self = this;

		homeNavPillContentView = new app.NavPillContentView();
		homeNavPillContentView.id = 'home';
		homeNavPillContentView.navPillsItemView = new app.NavPillsItemView({icon: "home", labelName: "Acceuil"});
		this.navPillContentViews.push(homeNavPillContentView);

		statsNavPillContentView = new app.NavPillContentView();
		statsNavPillContentView.id = 'stats';
		statsNavPillContentView.navPillsItemView = new app.NavPillsItemView({icon: "stats", labelName: "Statistique", path: "stats/"});
		this.navPillContentViews.push(statsNavPillContentView);

		messagesNavPillContentView = new app.NavPillContentView();
		messagesNavPillContentView.id = 'messages';
		messagesNavPillContentView.navPillsItemView = new app.NavPillsItemView({icon: "envelope", labelName: "Messages", path: "messages/"});
		this.navPillContentViews.push(messagesNavPillContentView);

		adsNavPillContentView = new app.NavPillContentView();
		adsNavPillContentView.id = 'ads';
		adsNavPillContentView.navPillsItemView = new app.NavPillsItemView({icon: "show_thumbnails_with_lines", labelName: "Annonces", path: "ads/"});
		this.navPillContentViews.push(adsNavPillContentView);

		settingsNavPillContentView = new app.NavPillContentView();
		settingsNavPillContentView.id = 'settings';
		settingsNavPillContentView.navPillsItemView = new app.NavPillsItemView({icon: "nameplate", labelName: "Paramètres", path: "settings/"});
		this.navPillContentViews.push(settingsNavPillContentView);

		_.each(this.navPillContentViews, function(view) {
			app.appRouter.on('route:'+view.id, self.switchPill, [self, view]);
		});
	},

	render: function() {
		var self = this;
		_.each(this.navPillContentViews, function(view) {
			self.renderPillItem(view);
		});
		return self;
	},

	renderPillItem: function(view) {
		this.$el.append(view.navPillsItemView.render().el);
	},

	selectPillItem: function() {
		this.selectedPillContentView.navPillsItemView.setActiveItem();
		this.trigger('navpillcontentselected:change');
	},

	unselectPillItem: function() {
		if (this.selectedPillContentView.navPillsItemView) this.selectedPillContentView.navPillsItemView.setUnactiveItem();
	},

	switchPill: function() {
		var self = this[0];
		var view = this[1];
		self.unselectPillItem();
		self.selectedPillContentView = view;
		self.selectPillItem();
	}

});