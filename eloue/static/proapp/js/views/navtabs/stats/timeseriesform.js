// js/views/navtabs/stats/timeseriesform.js


var app = app || {};


app.TimeSeriesForm = Backbone.View.extend({
	className: 'input-append range-date pull-right',

	template: _.template($("#timeseriesform-template").html()),

	events: {
		'click .btn.dropdown-toggle': 		'dropdown',
		'submit .form-inline': 				'submitForm',
	},

	render: function(){
		this.$el.html(this.template());
		return this;
	},

	dropdown: function(e) {
		e.stopPropagation();
		this.$el.children("div.btn-group").toggleClass('open');
		
		$('.dropdown-menu.pull-right').click(function(e) {
			e.stopPropagation();
		});

		var self = this;
		$('html').click(function(){
			self.$el.children("div.btn-group").removeClass('open');
		});
		delete self;
	},

	submitForm: function() {
		this.$el.children("div.btn-group").removeClass('open');
		console.log($("form.form-inline").serialize());
		return false;
	}
});