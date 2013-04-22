// js/collections/bills.js

var app = app || {};

app.BillsCollection = Backbone.Collection.extend({

	model: app.BillModel,

	url: API_URL.bills

});