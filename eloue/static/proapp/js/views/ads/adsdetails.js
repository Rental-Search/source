// js/views/ads/adsdetails.js

var app = app || {};

app.AdsDetailsView = Backbone.View.extend({
	className: 'list-main-content',

	model: null,

	template: _.template($("#ads-details-template").html()),


	serialize: function() {
		return {
			model: this.model.toJSON()
		}
	},

	render: function() {
		this.$el.html(this.template(this.serialize()));
		return this;
	}
});