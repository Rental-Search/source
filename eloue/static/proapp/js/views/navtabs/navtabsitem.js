// js/views/navtabs/navtabsitem.js

var app = app || {};

app.NavTabsItemView = Backbone.View.extend({
	tagName: 'li',

	template: _.template($("#navtabsitem-template").html()),

	path: null,

	icon: null,

	labelName: null,

	events: {
		'click a': 'selectedItem'
	},

	initialize: function() {
		if (this.options.path) this.path = this.options.path;
		if (this.options.icon) this.icon = this.options.icon;
		if (this.options.labelName) this.labelName = this.options.labelName;
	},

	render: function() {
		this.$el.html(this.template({'icon': this.icon, 'label': this.labelName, 'path': this.path}));
		return this;
	},

	setUnactiveItem: function() {
		this.$el.removeClass("active");
	},

	setActiveItem: function() {
		this.$el.addClass("active");
	},

	selectedItem: function(e) {
		e.preventDefault();
		this.trigger('selectedTabItem:change');
	}
});
