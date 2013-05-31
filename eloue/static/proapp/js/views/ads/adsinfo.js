// js/views/ads/adsinfo.js

var app = app || {};

app.AdsInfoView = Backbone.View.extend({
	item: app.NavTabItemView.extend({
		template: _.template($("#navbaritem-template").html()),
		icon: 'info-sign',
		path: null,
		labelName: 'Informations'
	}),

	render: function() {
		this.$el.html('<h1>Informations</h1>');
		return this;
	}
});