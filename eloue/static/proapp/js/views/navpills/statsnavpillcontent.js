// js/views/navpills/statsnavpillcontent.js

var app = app || {};


app.StatsNavPillContentView = app.NavPillContentView.extend({
	id: 'content-stats',

	className: 'content-pill tabbable tabs-left',

	navTabsView: null,

	currentNavTabContent: null,

	initialize: function() {
		this.navTabsView = new app.NavTabsView();
		this.navTabsView.pushNavTabContentViews(new app.NavTabsItemView({icon: 'dashboard', path: 'stats/', labelName: 'Vue d\'ensemble'}));
		this.navTabsView.pushNavTabContentViews(new app.NavTabsItemView({icon: 'user', path: 'stats/traffic/', labelName: 'Visites'}));
		this.navTabsView.pushNavTabContentViews(new app.NavTabsItemView({icon: 'phone', path: 'stats/phone/', labelName: 'Appels'}));
		this.navTabsView.pushNavTabContentViews(new app.NavTabsItemView({icon: 'link', path: 'stats/redirection/', labelName: 'Redirections'}));
	},

	setCurrentNavTabContentView: function(navTabContentView) {
		if (this.currentNavTabContent) {
			this.currentNavTabContent.close();
		}
		this.currentNavTabContent = navTabContentView;
	},

	render: function() {
		this.$el.prepend(this.navTabsView.$el);
		this.navTabsView.render();
		return this;
	},

	renderNavTabContent: function() {
		if (this.currentNavTabContent) {
			this.$el.append(this.currentNavTabContent.$el);
			this.currentNavTabContent.render();
		}
	},

	onClose: function() {
		this.navTabsView.close();
		if (this.currentNavTabContent) this.currentNavTabContent.close();
	}
});