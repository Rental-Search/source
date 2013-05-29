// js/views/core/nav.js

var app = app || {};

app.NavView = Backbone.View.extend({
	
	navTabViews: [],

	navTabItemsView: app.NavTabItemsView,

	selectedNavTabView: null,

	initialize: function() {},

	setSelectedNavTabViewAtIndex: function(index) {
		if( !_.isNull(this.selectedNavTabView) ) {
			if ( this.selectedNavTabView instanceof this.navTabViews[index] ) {
				return;
				console.log('return');
			} else {
				this.selectedNavTabView.close();
			}
		}
		
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
		this.setItems();
		this.$el.append(this.navTabItemsView.$el);
		this.navTabItemsView.render();
	},

	setItems: function() {
		var items = [];
		_.each(this.navTabViews, function(view) {
			items.push(view.prototype.item);
		});
		this.navTabItemsView = new this.navTabItemsView();
		this.navTabItemsView.items = items;
	},

	renderSelectedNavTabView: function() {
		this.$el.append(this.selectedNavTabView.$el);
		this.selectedNavTabView.render()
	},

	onClose: function() {
		if( !_.isNull(this.selectedNavTabView) ) this.navTabItemsView.close();
		if( !_.isNull(this.selectedNavTabView) ) this.selectedNavTabView.close();
	}
});