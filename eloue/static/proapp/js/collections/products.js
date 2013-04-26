// js/collections/products.js

var app = app || {};

app.ProductsCollection = Backbone.Collection.extend({

	model: app.ProductModel,

	url: API_URL.product

});