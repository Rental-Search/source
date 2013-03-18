// js/views/navpills.js

var app = app || {};


app.NavPillsView = Backbone.View.extend({
	tagName: 'ul',
	className: 'nav nav-pills  top-nav',

	navPillsItemViews: [],

	selectedPillItemView: '',

	pushNavPillItemView: function(view){
		this.navPillsItemViews.push(view);
		view.on('selectedPillItem:change', this.switchPill, [this, view]);
	},

	render: function() {
		var self = this;
		_.each(self.navPillsItemViews, function(view) {
			self.renderPillItem(view);
		});
		return self;
	},

	renderPillItem: function(view) {
		this.$el.append(view.$el);
		view.render();
	},

	selectPillItem: function(view) {
		this.selectedPillItemView = view;
		this.selectedPillItemView.setActiveItem();
	},

	unselectPillItem: function() {
		if (this.selectedPillItemView) {
			this.selectedPillItemView.setUnactiveItem();
		}
	},

	switchPill: function() {
		var self = this[0];
		var view = this[1];
		self.unselectPillItem();
		self.selectPillItem(view);
	}

});