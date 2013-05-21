// js/views/core/list.js

var app = app || {};

app.ListView = Backbone.View.extend({

	listItemsView: app.ListItemsView,

	detailView: null,

	initialize: function(){
		$(window).bind('resize.app', _.bind(this.resizeView, this));
	},

	setDetailViewWithId: function(id) {
		this.listItemsView.setSelectedItemWithId(id);
	},

	render: function() {
		this.resizeView();
		this.renderList();
		this.renderDetailView();
		return this;
	},

	renderList: function() {
		this.listItemsView = new this.listItemsView();
		this.listItemsView.on('selectedItem:change', this.renderDetailView, this);
		this.$el.append(this.listItemsView.$el);
		this.listItemsView.render();
	},

	renderDetailView: function() {
		if( !_.isNull(this.detailView) ) {
			if ( _.isFunction(this.detailView) ) this.detailView = new this.detailView();
			this.detailView.model = this.listItemsView.selectedItem;
			this.$el.append(this.detailView.$el);
			this.detailView.render();
		}
	},

	resizeView: function() {
		var proapp = $('#pro-app').height();
		var navpills = $('.nav-pills').height();
		if( !_.isNull(proapp) && !_.isNull(navpills) ) this.$el.height(proapp - navpills - 30);
	},

	onClose: function() {
		this.listItemsView.close();
		this.detailView.close();
	}
});