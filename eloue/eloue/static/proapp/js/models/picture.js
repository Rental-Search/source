// js/models/product.js

var app = app || {};

app.PictureModel = Backbone.Model.extend({

	validate: function(attrs, options) {
		var errors = [];

		return errors.length > 0 ? errors : false;
	},

});