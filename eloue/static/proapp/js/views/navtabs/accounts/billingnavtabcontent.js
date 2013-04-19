// js/views/navtabs/accounts/billingnavtabcontent.js

var app = app || {};


app.BillingNavTabContentView = app.AccountsNavTabContentView.extend({

	template: _.template($("#billingnavtabcontent-template").html()),

	model: app.BillModel,
});