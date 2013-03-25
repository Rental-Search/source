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

	serialize: function(timeseries) {
		var date1 = timeseries.start_date.split("-");
		var date2 = timeseries.end_date.split("-");

		return {
			timeseriesvalue : this._dateFrenchFormat(this._parseDate(date1)) + " - " + this._dateFrenchFormat(this._parseDate(date2)),
			start_date: timeseries.start_date.split("-").reverse().join("/"), 
			end_date: timeseries.end_date.split("-").reverse().join("/"), 
			interval: timeseries.interval.split("-").reverse().join("/")
		};
	},

	render: function(timeseries) {
		this.delegateEvents();
		this.$el.html(this.template(this.serialize(timeseries)));
		this.renderDatePicker();
		return this;
	},

	renderDatePicker: function() {
		$( "#datepicker" ).datepicker({
			numberOfMonths: 3,
			showCurrentAtPos: 0,
			maxDate: "d",
			onSelect: function(dateText, inst) {
				var selectedDate = new Date(inst.selectedYear, inst.selectedMonth, inst.selectedDay);
				var minDate = $(this).datepicker( "option", "minDate" );

				if ( minDate == null ) {
					$("input[name=start_date]").focus();
					$(this).datepicker( "option", "minDate", selectedDate);
					$("input[name=start_date]").val(dateText);
					$("input[name=end_date]").focus();
					
				} 

				if  (minDate != null && minDate.getTime() == selectedDate.getTime()) {
					$("input[name=start_date]").focus();
					$(this).datepicker( "option", "minDate", "");
				}

				if ( minDate != null ) {
					$("input[name=end_date]").val(dateText);
					$("input[name=start_date]").focus();
				}
			},

			beforeShowDay: function(date) {
				var startDate = $.datepicker.parseDate('dd/mm/yy', $("input[name=start_date]").val().toString());
				var endDate = $.datepicker.parseDate('dd/mm/yy', $("input[name=end_date]").val().toString());

				console.log( startDate );
				console.log( endDate );

				if ( startDate != null && endDate != null ) {
					if ( date.getTime() >= startDate.getTime() && date.getTime() <= endDate.getTime()) {
						return [true, "highlighted"];
					}
				}

				return [true, ""];
			}
		});

		$("input[name=start_date]").bind("focus", function() {
			$("#datepicker").datepicker( "option", "minDate", null );
		});
	},

	toggleDropdown: function(e) {
		e.stopPropagation();
		this.$el.children("div.btn-group").toggleClass('open');
		$("button[type=submit].btn.btn-small").attr("disabled", "disabled");

		
		$('.dropdown-menu.pull-right').click(function(e) {
			e.stopPropagation();
		});

		var self = this;
		$('html').click(function(){
			self.$el.children("div.btn-group").removeClass('open');
		});

		$("input[name=start_date]").focus();
		this.validateInput();

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

	serializeForm: function() {
		return $("form.form-inline").serialize();
	},

	_parseDate: function(date) {
		return new Date(date[0],date[1]-1,date[2]);
	},

	_dateFrenchFormat: function(date) {
		var months = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"];
		return date.getDate() + " " + months[date.getMonth()] + " " + date.getFullYear();
	}
});