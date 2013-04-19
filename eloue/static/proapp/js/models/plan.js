// js/models/plan.js

var app = app || {};

app.PlanModel = Backbone.Model.extend({

	validate: function(attrs, options) {
		var errors = [];

		return errors.length > 0 ? errors : false;
	},

});