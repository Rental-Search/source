// js/models/plan.js

var app = app || {};

app.SubscriptionModel = Backbone.Model.extend({

	urlRoot: API_URL.subscription,


	validate: function(attrs, options) {
		var errors = [];

		return errors.length > 0 ? errors : false;
	},

});