// js/views/ads/adsinfo.js

var app = app || {};

app.AdsInfoView = Backbone.View.extend({
	model: null,

	template: _.template($("#ads-info-template").html()),

	item: app.NavTabItemView.extend({
		template: _.template($("#navbaritem-template").html()),
		icon: 'info-sign',
		path: null,
		labelName: 'Informations'
	}),

	initialize: function() {
		this.loadingView = new app.LoadingView();
	},

	setModel: function(model) {
		this.model = model;
		this.model.on('request', this.renderLoadingView, this);
		this.model.on('sync', this.renderContent, this);
		this.renderContent();
	},

	serialize: function() {
		return {
			model: this.model.toJSON()
		}
	},

	render: function() {
		this.renderLoadingView();
		return this;
	},

	renderLoadingView: function() {
		this.$el.html(this.loadingView.$el);
		this.loadingView.render();
	},

	renderContent: function() {
		this.$el.html(this.template(this.serialize()));
	},

	onClose: function() {
		this.loadingView.close();
		this.model.unbind();
	}

});