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

	initialize: function() {},

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
		
	},

	selectItem: function(e) {
		e.preventDefault();
		var id = $(e.currentTarget).attr('id');
		app.appRouter.navigate('ads/' + id +'/', {trigger: true});
	},

	setSelectedItemWithId: function(id) {
		this.selectedItem = this.collection.get(id);
		this.activeSelectedItem();
	},

	activeSelectedItem: function() {
		this.unactiveSelectedItem();
		if( !_.isUndefined(this.selectedItem) ) {
			$('#' + this.selectedItem.id ).parent().addClass('active');
		}
	},

	unactiveSelectedItem: function() {
		this.$el.children().children().removeClass('active');
	},	

	onClose: function() {
		if( !_.isNull(this.collection) ) {
			this.collection.unbind();
		}
	}
});