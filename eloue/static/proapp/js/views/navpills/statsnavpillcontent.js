// js/views/navpills/statsnavpillcontent.js

var app = app || {};


app.StatsNavPillContentView = app.NavPillContentView.extend({
	id: 'content-stats',

	className: 'content-pill tabbable tabs-left',

	navTabsView: null,

	currentNavTabContent: null,

	timeSeries: null,

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
		this.currentNavTabContent.on('timeSeries:change', this.updateTimeSeries, this);
		this.currentNavTabContent.setTimeSeriesView(this.timeSeries);
	},

	updateTimeSeries: function () {
		this.timeSeries = this.currentNavTabContent.timeSeries;
	},

	render: function() {
		this.renderNavTabs();
		return this;
	},

	renderNavTabs: function() {
		this.$el.prepend(this.navTabsView.$el);
		this.navTabsView.render();
	},

	renderNavTabContent: function() {
		if (this.currentNavTabContent) {
			this.$el.append(this.currentNavTabContent.$el);
		}
	},

	onClose: function() {
		this.navTabsView.close();
		if (this.currentNavTabContent) this.currentNavTabContent.close();
	}
});