// js/views/navtabs/navtabcontent.js

var app = app || {}

app.NavTabContentView = Backbone.View.extend({
	className: 'tab-content',

	titleName: '',

	initialize: function() {
		if (this.options.titleName) this.titleName = this.options.titleName;
	},

	render: function() {
		this.$el.html("<h3>" + this.titleName + "<h3>");
		this.$el.height(400);
		return this;
	}
});