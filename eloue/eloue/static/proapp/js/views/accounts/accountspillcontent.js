// js/view/accounts/accountspillcontent.js

var app = app || {};

app.AccountsPillContentView = app.NavView.extend({
	id: 'content-accounts',

	className: 'content-pill tabbable tabs-left',

	item: app.NavTabItemView.extend({
		template: _.template($("#navpillsitem-template").html()),

		path: 'accounts/', 

		icon: 'nameplate', 

		labelName: 'Compte'
	}),

	initialize: function() {
		//Extend the class name for navtabs
		this.navTabItemsView = this.navTabItemsView.extend({className:  'nav nav-tabs border-right'});

		this.navTabViews = [app.PatronTabContentView, app.ShopTabContentView, app.BillingTabContentView, app.PlanTabContentView];
	}
});