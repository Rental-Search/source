// js/views/navtabs/navtabcontent.js

var app = app || {}

app.NavTabContentView = Backbone.View.extend({
	className: 'tab-content',

	navTabsItemView: '',

	initialize: function() {
		console.log("init tab content")
	},

	render: function() {
		console.log("render tab content");
		this.$el.html("<h3>" + this.navTabsItemView.labelName + '<h3>');
		this.$el.height(400);
		return this;
	}
});