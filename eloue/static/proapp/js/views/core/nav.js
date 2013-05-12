// js/views/core/nav.js

var app = app || {};

app.NavView = Backbone.View.extend({
	
	navTabViews: [],

	navTabItemsView: app.NavTabItemsView,

	selectedNavTabView: null,

	initialize: function() {},

	setSelectedNavTabViewAtIndex: function(index) {
		if( !_.isNull(this.selectedNavTabView) ) this.selectedNavTabView.close();

		this.navTabItemsView.setSelectedItemAtIndex(index);
		this.selectedNavTabView = new this.navTabViews[index]();
		this.trigger('selectedNavTabView:change');
		this.renderSelectedNavTabView();
	},

	render: function() {
		this.renderNavTabItems();
		return this;
	},

	renderNavTabItems: function() {
		var items = [];
		_.each(this.navTabViews, function(view) {
			items.push(view.prototype.item);
		});
		this.navTabItemsView = new this.navTabItemsView();
		this.navTabItemsView.items = items;
		this.$el.append(this.navTabItemsView.render().$el)
	},

	renderSelectedNavTabView: function() {
		this.$el.append(this.selectedNavTabView.render().$el);
	},

	onClose: function() {
		this.navTabItemsView.close();
		this.selectedNavTabView.close();
	}
});