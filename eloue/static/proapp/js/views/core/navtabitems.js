// js/views/core/navtabitems.js

var app = app || {};

app.NavTabItemsView = Backbone.View.extend({
	tagName: 'ul',

	items: [],

	selectedItem: null,


	initialize: function() {},

	setSelectedItemAtIndex: function(index) {
		if ( !_.isNull(this.selectedItem) ) this.unselectItem();
		this.selectedItem = this.items[index];
		this.selectItem();
	},

	render: function() {
		var self = this;
		_.each(self.items, function(item, index) {
			self.items[index] = new item();
			self.renderItem(self.items[index]);
		});
		return this;
	},

	renderItem: function(item) {
		this.$el.append(item.$el);
		item.render();
	},

	unselectItem: function() {
		this.selectedItem.unactive();
	},

	selectItem: function() {
		this.selectedItem.active();
	},

	onClose: function() {
		_.each(this.items, function(item) {
			item.close();
		});
	}
});