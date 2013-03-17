// js/views/navpills.js

var app = app || {};


app.NavPillsView = Backbone.View.extend({
	tagName: 'ul',
	className: 'nav nav-pills  top-nav',

	navPillContentViews: [],

	selectedPillContentView: '',

	pushNavPillContentViews: function(view) {
		this.navPillContentViews.push(view);
		app.appRouter.on('route:'+view.id, this.switchPill, [this,view]);
	},

	render: function() {
		var self = this;
		_.each(this.navPillContentViews, function(view) {
			self.renderPillItem(view);
		});
		return self;
	},

	renderPillItem: function(view) {
		this.$el.append(view.navPillsItemView.render().el);
	},

	selectPillItem: function(view) {
		this.selectedPillContentView = view;
		this.selectedPillContentView.navPillsItemView.setActiveItem();
		this.trigger('navpillcontentselected:change');
	},

	unselectPillItem: function() {
		if (this.selectedPillContentView.navPillsItemView) {
			this.selectedPillContentView.navPillsItemView.setUnactiveItem();
		}
	},

	switchPill: function() {
		var self = this[0];
		var view = this[1];
		self.unselectPillItem();
		self.selectPillItem(view);
	}

});