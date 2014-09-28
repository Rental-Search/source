// js/views/ads/adspic.js

var app = app || {};

app.AdsPicView = Backbone.View.extend({
	model: null,

	collection: app.PicturesCollection,

	template: _.template($("#ads-pictures-template").html()),


	item: app.NavTabItemView.extend({
		template: _.template($("#navbaritem-template").html()),
		icon: 'picture',
		path: null,
		labelName: 'Images'
	}),

	initialize: function() {
		this.loadingView = new app.LoadingView();
	},

	setModel: function(model) {
		this.model = model;
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