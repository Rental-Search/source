// js/views/list/navcontent.js

var app = app || {};

app.NavContentView = Backbone.View.extend({
	className: 'nav-container',

	template: _.template($("#nav-content-template").html()),

	model: null,

	initialize: function() {
		this.model = this.options.model;
		this.model.on('sync', this.render, this);
		$(window).bind("resize.app", _.bind(this.resizeView, this));
	},

	serialize: function() {
		return {
			model: this.model.toJSON()
		}
	},

	render: function() {
		this.resizeView();
		this.$el.html(this.template(this.serialize()));
		return this;
	},

	resizeView: function() {
		var mainContent = $('.list-main-content').height();
		var navbar = $('.navbar').height();
		if( !_.isNull(mainContent) && !_.isNull(navbar) ) this.$el.height(mainContent - navbar);
	},

	onclose: function() {
		this.model.unbind();
	}
});