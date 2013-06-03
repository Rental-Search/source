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
		if( !_.isNull(id) ) {
			if( !_.isNull(this.selectedDetailView) ) {
				if (!_.isNull(this.selectedDetailView.model)) {
					if ( this.selectedDetailView.model.id == parseInt(id) ) {
						callback();
						return;
					} else {
						this.selectedDetailView.close();
					}
				} else {
					this.selectedDetailView.close();
				}
			}

			this.once("selectedDetailView:rendered", callback, this);

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
		} else {
			this.renderNoSelectedDetailView();
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

	renderNoSelectedDetailView: function() {
		this.selectedDetailView = new this.detailView();
		this.$el.append(this.selectedDetailView.$el);
		this.selectedDetailView.render();
	},

	renderSelectedDetailView: function() {
		this.selectedDetailView = new this.detailView();
		this.selectedDetailView.setModel(this.listItemsView.selectedItem);
		this.$el.append(this.selectedDetailView.$el);
		this.selectedDetailView.render();
		this.trigger("selectedDetailView:rendered");
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