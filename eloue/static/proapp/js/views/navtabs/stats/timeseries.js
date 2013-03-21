// js/views/navtabs/stats/timeseries.js


var app = app || {};


app.TimeSeriesView = Backbone.View.extend({
	className: 'input-append range-date pull-right',

	template: _.template($("#timeseriesform-template").html()),

	events: {
		'click .btn.dropdown-toggle': 	'toggleDropdown',
		'keyup	input.input-small': 	'validateInput', 
		'submit .form-inline':			'submitForm',
	},

	render: function(){
		this.delegateEvents();
		this.$el.html(this.template());
		return this;
	},

	toggleDropdown: function(e) {
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

	validateInput: function(e) {
		$('input.input-small').removeClass('error');
		$("button[type=submit].btn.btn-small").removeAttr("disabled");

		var start_date = this._parseDate($("input[name=start_date]").val().split("/").reverse());
		var end_date = this._parseDate($("input[name=end_date]").val().split("/").reverse());

		if (start_date > end_date || $(e.currentTarget).val().match(/^\d\d?\/\d\d?\/\d\d\d\d$/) == null) {
			$(e.currentTarget).addClass('error');
			$("button[type=submit].btn.btn-small").attr("disabled", "disabled");
		}
	},

	submitForm: function() {
		this.$el.children("div.btn-group").removeClass('open');
		this.trigger('timeseriesform:submited')
		return false;
	},

	serialize: function() {
		return $("form.form-inline").serialize();
	},

	_parseDate: function(date) {
		return new Date(date[0],date[1]-1,date[2]);
	}
});