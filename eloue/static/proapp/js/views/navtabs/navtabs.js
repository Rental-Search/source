// js/views/navtabs/navtabs.js

var app = app || {}

app.NavTabsView = Backbone.View.extend({
	tagName: 'ul',
	className: 'nav nav-tabs',

	navTabsItemViews: null,

	selectedTabItemView: null,

	initialize: function() {
		this.navTabsItemViews = [];
	},

	pushNavTabContentViews: function(view) {
		this.navTabsItemViews.push(view);
		view.on('selectedTabItem:change', this.switchTab, [this,view]);
	},

	render: function() {
		var self = this;
		_.each(self.navTabsItemViews, function(view) {
			self.renderTabItem(view);
		});
		delete self;
		return this;
	},

	renderTabItem: function(view) {
		this.$el.append(view.$el);
		view.render();
	},

	selectTabItem: function(view) {
		this.selectedTabItemView = view;
		this.selectedTabItemView.setActiveItem();
	},

	unselectTabItem: function() {
		if( this.selectedTabItemView) {
			this.selectedTabItemView.setUnactiveItem();
		}
			
	},

	switchTab: function() {
		var self = this[0];
		var view = this[1];
		self.unselectTabItem();
		self.selectTabItem(view);
		delete self;
		delete view;
	},

	onClose: function() {
		_.each(this.navTabsItemViews, function(view) {
			view.close();
		});
	}
});