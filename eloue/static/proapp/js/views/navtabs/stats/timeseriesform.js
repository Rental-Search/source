// js/views/navtabs/stats/timeseriesform.js


var app = app || {};


app.TimeSeriesForm = Backbone.View.extend({
	className: 'input-append range-date',

	template: _.template($("#timeseriesform-template").html()),

	events: {
		'click .btn.dropdown-toggle': 	'dropdown',
		'submit .form-inline': 			'submitForm',
	},

	render: function(){
		this.$el.html(this.template());
		return this;
	},

	dropdown: function() {
		this.$el.children("div.btn-group").toggleClass('open');
	},

	submitForm: function() {
		console.log("")
		this.$el.children("div.btn-group").removeClass('open');
		return false;
	}
});