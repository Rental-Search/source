// js/models/product.js

var app = app || {};

app.ProductModel = Backbone.Model.extend({

	url: API_URL.product,

	validate: function(attrs, options) {
		var errors = [];

		return errors.length > 0 ? errors : false;
	},

});