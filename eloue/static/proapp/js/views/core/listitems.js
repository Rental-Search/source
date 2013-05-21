// js/views/core/listitems.js

var app = app || {};

app.ListItemsView = Backbone.View.extend({
	className: 'list-side-content',

	template: _.template($("#list-template").html()),

	collection: null,

	selectedItem: null,

	events: {
		'click a': 'selectItem'
	},

	initialize: function() {
		this.on('selectedItem:change', this.activeSelectedItem, this);
	},

	serialize: function() {
		return {
			collection: this.collection.toJSON()
		}
	},

	render: function() {
		if( !_.isNull(this.collection) ) {
			this.collection = new this.collection();
			this.collection.on('sync', this.renderItems, this);
			this.collection.fetch();
		}
		return this;
	},

	renderItems: function() {
		this.$el.html(this.template(this.serialize()));
		//if selectedItem is a string and not an object so we selected the item
		if( _.isString(this.selectedItem) ) this.setSelectedItemWithId(this.selectedItem);
	},

	selectItem: function(e) {
		e.preventDefault();
		var id = $(e.currentTarget).attr('id');
		app.appRouter.navigate('ads/' + id +'/', {trigger: true});
	},

	setSelectedItemWithId: function(id) {
		this.selectedItem = this.collection.get(id);
		//if collection is not fetched we just id is stock
		if ( _.isUndefined(this.selectedItem) ) this.selectedItem = id; 
		else this.trigger('selectedItem:change');	
	},

	activeSelectedItem: function() {
		this.$el.children().children().removeClass('active');
		if( !_.isUndefined(this.selectedItem) ) {
			$('#' + this.selectedItem.id ).parent().addClass('active');
		}
	},

	onClose: function() {
		if( !_.isNull(this.collection) ) {
			this.collection.unbind();
		}
	}
});