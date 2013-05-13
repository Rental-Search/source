// js/views/accounts/billingtabcontent.js

var app = app || {};

app.BillingTabContentView = app.AccountsTabContentView.extend({
	
	titleName: 'Facturation',

	item: app.NavTabItemView.extend({
		template: _.template($("#navtabsitem-template").html()),
		icon: 'euro', 
		path: 'accounts/billing/', 
		labelName: 'Facturation'
	}),
	
	model: app.BillModel,

	template: _.template($("#billingnavtabcontent-template").html()),
});