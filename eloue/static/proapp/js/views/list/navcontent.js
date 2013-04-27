// js/views/list/navcontent.js

var app = app || {};

app.NavContentView = Backbone.View.extend({
	className: 'nav-content',

	template: _.template($("#nav-content-template").html()),

	model: null,

	initialize: function() {
		this.model = this.options.model;
		this.model.on('sync', this.render, this);
	},

	serialize: function() {
		return {
			model: this.model.toJSON()
		}
	},

	render: function() {
		console.log("render content of navcontent");
		this.$el.html(this.template(this.serialize()));
		return this;
	},

	onclose: function() {
		this.model.unbind();
	}
});