// js/views/navpills/navpillcontent.js

var app = app || {};


app.NavPillContentView = Backbone.View.extend({
	className: 'content-pill',

	template: _.template($("#navpillcontent-template").html()),

	initialize: function() {

	},

	render: function() {
		this.$el.html(this.template({'name': this.id }));
		return this;
	}
});