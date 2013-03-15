// js/views/navpillsitem.js

var app = app || {};


app.NavPillContentView = Backbone.View.extend({
	className: 'content-pill',

	template: _.template($("#navpillcontent-template").html()),

	navPillsItemView: '',

	initialize: function() {

	},

	render: function() {
		this.$el.html(this.template({'name': this.navPillsItemView.labelName}));
		return this;
	}
});