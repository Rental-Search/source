// js/views/navpills/adsnavpillcontent.js

var app = app || {};

app.AdsNavPillContentView = app.NavPillContentView.extend({
	id: 'ads',

	className: 'content-pill clearfix',

	currentDetailContent: null,

	initialize: function() {
		this.listView = new app.ListView({collection: app.ProductsCollection});
		this.listDetailView = new app.ListDetailView();
		
		this.listView.collection.on('sync', this.resizeView, this);
		$(window).bind('resize.app', _.bind(this.resizeView, this));
	},

	render: function() {
		this.resizeView();
		this.$el.html(this.listView.el);
		return this;
	},

	renderDetail: function(id) {
		if ( _.isUndefined(id) ) {
			this.listDetailView.model = null;
		} else {
			this.listDetailView.model = this.listView.collection.findWhere({id: id.toString()});
		}
		this.$el.append(this.listDetailView.render().el);
	},

	resizeView: function() {
		var proapp = $('#pro-app').height();
		var navpills = $('.nav-pills').height();
		if( !_.isNull(proapp) && !_.isNull(navpills) ) this.$el.height(proapp - navpills - 30);
	},

	onClose: function() {
		$(window).unbind("resize.app");
		this.listView.close();
	}
});