// js/models/shop.js

var app = app || {};

app.ShopModel = Backbone.Model.extend({

	urlRoot: API_URL.shop,


	validate: function(attrs, options) {
		var errors = [];

		return errors.length > 0 ? errors : false;
	},

});