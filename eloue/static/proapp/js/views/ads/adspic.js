// js/views/ads/adspic.js

var app = app || {};

app.AdsPicView = Backbone.View.extend({
	item: app.NavTabItemView.extend({
		template: _.template($("#navbaritem-template").html()),
		icon: 'picture',
		path: null,
		labelName: 'Images'
	}),

	render: function() {
		this.$el.html('<h1>Images</h1>');
		return this;
	}
});