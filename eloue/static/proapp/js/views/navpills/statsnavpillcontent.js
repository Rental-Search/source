// js/views/navpills/statsnavpillcontent.js

var app = app || {};


app.StatsNavPillContentView = app.NavPillContentView.extend({
	className: 'content-pill tabbable tabs-left',

	initialize: function() {
		console.log("init stats content pill");

		this.statsNavtabsView = new app.NavTabsView();
		
		var overviewNavTabContentView = new app.NavTabContentView()
		overviewNavTabContentView.navTabsItemView = new app.NavTabsItemView({icon: 'dashboard', path: 'stats/', labelName: 'Vue d\'ensemble'});
		this.statsNavtabsView.pushNavTabContentViews(overviewNavTabContentView);

		var trafficNavTabContentView = new app.NavTabContentView()
		trafficNavTabContentView.navTabsItemView = new app.NavTabsItemView({icon: 'user', path: 'stats/traffic/', labelName: 'Visite'});;
		this.statsNavtabsView.pushNavTabContentViews(trafficNavTabContentView);

		var phoneNavTabContentView = new app.NavTabContentView()
		phoneNavTabContentView.navTabsItemView = new app.NavTabsItemView({icon: 'phone', path: 'stats/phone/', labelName: 'Appels'});;
		this.statsNavtabsView.pushNavTabContentViews(phoneNavTabContentView);

		this.statsNavtabsView.selectTabItem(overviewNavTabContentView);
	},

	render: function() {
		this.statsNavtabsView.on('selectedtabcontentview:change', this.renderTabContent, this);
		this.renderNavTabs();
		this.renderTabContent();
		return this;
	},

	renderNavTabs: function() {
		this.$el.append(this.statsNavtabsView.$el);
		this.statsNavtabsView.render();
	},

	renderTabContent: function() {
		this.$el.append(this.statsNavtabsView.selectedTabContentView.render().el)
	}
});