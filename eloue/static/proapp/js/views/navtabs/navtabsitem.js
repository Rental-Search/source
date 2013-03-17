// js/views/navtabs/navtabsitem.js

var app = app || {};

app.NavTabsItemView = Backbone.View.extend({
	tagName: 'li',

	template: _.template($("#navtabsitem-template").html()),

	path: '',

	icon: '',

	labalName: '',

	events: {
		'click a': 'selectedItem'
	},

	initialize: function() {
		if (this.options.path) this.path = this.options.path;
		if (this.options.icon) this.icon = this.options.icon;
		if (this.options.labelName) this.labelName = this.options.labelName;
	},

	render: function() {
		console.log("render item tab");
		this.delegateEvents();
		this.$el.html(this.template({'icon': this.icon, 'label': this.labelName, 'path': this.path}));
		return this;
	},

	setActiveItem: function() {
		this.$el.addClass("active");
	},

	setUnactiveItem: function() {
		this.$el.removeClass("active");
	},

	selectedItem: function(e) {
		console.log("click on tab");
		e.preventDefault();
		this.trigger('navtabsitemview:selected');
	}
});
