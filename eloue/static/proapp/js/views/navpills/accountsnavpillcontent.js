// js/views/navpills/accountsnavpillcontent.js

var app = app || {};


app.AccountsNavPillContentView = app.NavPillContentView.extend({
	id: 'content-accounts',

	className: 'content-pill tabbable tabs-left',

	navTabsView: null,

	currentNavTabContent: null,

	timeSeries: null,

	initialize: function() {
		this.navTabsView = new app.NavTabsView();
		this.navTabsView.pushNavTabContentViews(new app.NavTabsItemView({icon: 'user', path: 'accounts/', labelName: 'Informations'}))
		this.navTabsView.pushNavTabContentViews(new app.NavTabsItemView({icon: 'euro', path: 'accounts/billing/', labelName: 'Facturation'}))
	},

	setCurrentNavTabContentView: function(navTabContentView) {
		if (this.currentNavTabContent) {
			this.currentNavTabContent.close();
		}
		this.currentNavTabContent = navTabContentView;
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
})