// js/views/core/list.js

var app = app || {};

app.ListView = Backbone.View.extend({

	listItemsView: app.ListItemsView,

	detailView: null,

	selectedDetailView: null,

	initialize: function(){
		$(window).bind('resize.app', _.bind(this.resizeView, this));
		this.listItemsView = new this.listItemsView();
	},

	setDetailViewWithId: function(id, callback) {
		if( !_.isNull(this.selectedDetailView) ) {
			if ( this.selectedDetailView.model.id == parseInt(id) ) {
				return;
			} else {
				this.selectedDetailView.close();
			}
		}

		// Waiting the result of the fetch before render the detail view
		if( this.listItemsView.collection.length == 0 ) {
			this.listItemsView.collection.once('sync', function() {
				this.listItemsView.setSelectedItemWithId(id);
				this.renderSelectedDetailView();
			}, this);
		} else {
			this.listItemsView.setSelectedItemWithId(id);
			this.renderSelectedDetailView();
		}
	},

	render: function() {
		this.resizeView();
		this.renderList();
		return this;
	},

	renderList: function() {
		this.$el.append(this.listItemsView.$el);
		this.listItemsView.render();
	},

	renderSelectedDetailView: function() {
		this.selectedDetailView = new this.detailView();
		this.selectedDetailView.model = this.listItemsView.selectedItem;
		this.$el.append(this.selectedDetailView.$el);
		this.selectedDetailView.render();
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