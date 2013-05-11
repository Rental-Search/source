// js/views/core/navtabcontent.js

var app = app || {};

app.NavTabView = Backbone.View.extend({

	item: null,

	onClose: function() {
		console.log("tabcontent on close");
	}
});