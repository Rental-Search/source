// js/views/loading.js


var app = app || {};


app.LoadingView = Backbone.View.extend({
	className: 'loading',

	template: _.template($("#loading-template").html()),

	render: function() {
		console.log('render loading');
		this.$el.html(this.template());
	}
});
