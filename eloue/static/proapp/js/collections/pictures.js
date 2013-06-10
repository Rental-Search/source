// js/collections/products.js

var app = app || {};

app.PicturesCollection = Backbone.Collection.extend({

	model: app.PictureModel,

	url: API_URL.picture

});