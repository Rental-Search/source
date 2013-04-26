// js/views/list/listdetail.js

var app = app || {};

app.ListDetailView = Backbone.View.extend({
	className: 'list-main-content',

	template: _.template($("#list-detail-template").html()),

	model: null,

	currentNavContent: null,

	initialize: function() {
		if( !_.isNull(this.model) ) this.currentNavContent = new app.NavContentView({model: this.model});	
	},

	serialize: function() {
		var data;
		if( _.isNull(this.model) ) data = null;
		else data = this.model.toJSON();
		return {model: data}
	},

	render: function() {
		this.$el.html(this.template(this.serialize()));
		if( _.isNull(this.model) ) this.renderNavContent();
		return this;
	},

	renderNavContent: function() {
		console.log("render nav content");
	},

	onClose: function() {
		this.model.unbind();
		this.currentNavContent.close();
	}
});
