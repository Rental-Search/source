// js/views/core/list.js

var app = app || {};

app.ListView = Backbone.View.extend({

	listItemsView: app.ListItemsView,

	detailView: null,

	selectedDetailView: null,

	initialize: function(){
		$(window).bind('resize.app', _.bind(this.resizeView, this));
	},

	setDetailViewWithId: function(id, callback) {
		if( !_.isNull(this.selectedDetailView) ) {
			if ( this.selectedDetailView.collection.id == int(id) ) {
				return;
			} else {
				this.selectedDetailView.close();
			}
		}
		//this.listItemsView.setSelectedItemWithId(id);
		//this.selectedDetailView = new this.detailView();
	},

	render: function() {
		this.resizeView();
		this.renderList();
		return this;
	},

	renderList: function() {
		this.listItemsView = new this.listItemsView();
		this.listItemsView.on('selectedItem:change', this.renderSelectedDetailView, this);
		this.$el.append(this.listItemsView.$el);
		this.listItemsView.render();
	},

	renderSelectedDetailView: function() {
		//this.selectedDetailView.model = this.listItemsView.selectedItem;
		//this.$el.append(this.selectedDetailView.$el);
		//this.selectedDetailView.render();
	},

	resizeView: function() {
		var proapp = $('#pro-app').height();
		var navpills = $('.nav-pills').height();
		if( !_.isNull(proapp) && !_.isNull(navpills) ) this.$el.height(proapp - navpills - 30);
	},

	onClose: function() {
		if( !_.isNull(this.listItemsView) ) this.listItemsView.close();
		if( !_.isNull(this.selectedDetailView) )this.selectedDetailView.close();
	}
});