// js/views/navtabs/navtabcontent.js

var app = app || {}

app.NavTabContentView = Backbone.View.extend({
	className: 'tab-content',

	navTabsItemView: '',

	render: function() {
		this.$el.html("<h3>" + this.navTabsItemView.labelName + '<h3>');
		this.$el.height(400);
		return this;
	}
});