// js/views/ads/adspillcontent.js

var app = app || {};

app.AdsPillContentView = app.ListView.extend({
	id:'content-ads',

	className: 'content-pill clearfix',

	item: app.NavTabItemView.extend({
		template: _.template($("#navpillsitem-template").html()),

		path: 'ads/', 

		icon: 'show_thumbnails_with_lines', 

		labelName: 'Annonces'
	}),

	initialize: function() {
		this.constructor.__super__.initialize.apply(this, [this.options]);
		this.listItemsView = this.listItemsView.extend({
			collection: app.ProductsCollection
		});

		// this.detailView = Backbone.View.extend({
		// 	className: 'list-main-content',

		// 	model: null,

		// 	render: function() {
		// 		this.$el.html('<h1>' + this.model.toJSON().summary + '</h1>');
		// 		return this;
		// 	}
		// });

		this.detailView = new app.AdsDetailsView;
	}
});