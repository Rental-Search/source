// js/views/ads/adsprice.js

var app = app || {};

app.AdsPriceView = Backbone.View.extend({
	
	item: app.NavTabItemView.extend({
		template: _.template($("#navbaritem-template").html()),
		icon: 'calendar',
		path: null,
		labelName: 'Tarifs et disponibilités'
	}),

	render: function() {
		this.$el.html('<h1>Tarifs et disponibilités</h1>');
		return this;
	}
});