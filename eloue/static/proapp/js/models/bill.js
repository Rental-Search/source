// js/models/bill.js

var app = app || {};

app.BillModel = Backbone.Model.extend({

	urlRoot: API_URL.bills,

	validate: function(attrs, options) {
		var errors = [];

		return errors.length > 0 ? errors : false;
	},

});