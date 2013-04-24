// js/views/list/listdetail.js

var app = app || {};

app.ListDetailView = Backbone.View.extend({
	className: 'list-main-content',

	template: _.template($("#list-detail-template").html()),

	model: null,

	initialize: function() {},

	serialize: function() {
		var data;
		if( _.isNull(this.model) ) data = null;
		else data = this.model.toJSON();
		return {model: data}
	},

	render: function() {
		this.$el.html(this.template(this.serialize()));

		return this;
	}
});
