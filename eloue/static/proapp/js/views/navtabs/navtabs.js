// js/views/navtabs/navtabs.js

var app = app || {}

app.NavTabsView = Backbone.View.extend({
	tagName: 'ul',
	className: 'nav nav-tabs',

	navTabContentViews: [],

	selectedTabContentView: '',

	initialize: function() {

	},

	pushNavTabContentViews: function(view) {
		this.navTabContentViews.push(view);
		view.navTabsItemView.on('navtabsitemview:selected', this.switchTab, [this,view]);
	},

	render: function() {
		self = this;
		_.each(self.navTabContentViews, function(view) {
			self.$el.append(view.navTabsItemView.render().el);
		});
		return self;
	},

	selectTabItem: function(view) {
		this.selectedTabContentView = view;
		this.selectedTabContentView.navTabsItemView.setActiveItem();
		this.trigger('selectedtabcontentview:change');
	},

	unselectTabItem: function() {
		if( this.selectedTabContentView.navTabsItemView) this.selectedTabContentView.navTabsItemView.setUnactiveItem();
	},

	switchTab: function() {
		var self = this[0];
		var view = this[1];
		self.unselectTabItem();
		self.selectTabItem(view);
	}
});