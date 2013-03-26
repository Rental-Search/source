// js/views/navtabs/stats/timeseries.js

var app = app || {};


app.TimeSeriesView = Backbone.View.extend({
	className: 'input-append range-date pull-right',


	template: _.template($("#timeseriesform-template").html()),

	events: {
		'click	button.btn.dropdown-toggle': 	'toggleDropdown',
		'keyup	input.input-small': 			'validateInput', 
		'submit form.form-inline':				'submitForm',
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
		var datePicker = $( "#datepicker" );
		var minD = null
		datePicker.datepicker({
			numberOfMonths: 3,
			maxDate: "d",
			onSelect: function(dateText, inst) {

				var selectedDate = new Date(inst.selectedYear, inst.selectedMonth, inst.selectedDay);
				if ( minD == null ) {
					$("input[name=start_date]").focus();
					$("input[name=start_date]").val(dateText);
					$("input[name=end_date]").focus();
				} else if ( minD != null && minD.getTime() == selectedDate.getTime() && $("input[name=start_date]") == true ) {
					$("input[name=start_date]").focus();
				} else if ( minD != null ) {
					$("input[name=end_date]").val(dateText);
					$("input[name=start_date]").focus();
				}
			},
			beforeShowDay: function(date) {
				var startDate = $.datepicker.parseDate('dd/mm/yy', $("input[name=start_date]").val().toString());
				var endDate = $.datepicker.parseDate('dd/mm/yy', $("input[name=end_date]").val().toString());
				
				if ( startDate != null && endDate != null ) {
					if ( minD != null ) {
						if ( date.getTime() < startDate ) {
							return [false, ""];
						}
					} else if ( date.getTime() >= startDate.getTime() && date.getTime() <= endDate.getTime()) {
						return [true, "highlighted"];
					} else {
						return [true, ""];
					}
				}

				return [true, ""];
			},
		});

		$("input[name=start_date]").bind("focus", function() {
			minD = null;
			$("#datepicker").datepicker( "refresh" );
		});

		$("input[name=end_date]").bind("focus", function() {
			minD = $.datepicker.parseDate('dd/mm/yy', $("input[name=start_date]").val().toString());
			$("#datepicker").datepicker( "refresh" );
		});

		//select today range dates
		$("a[href=#today-link]").bind("click", function(e){
			e.preventDefault();
			minD = null;
			var date = new Date();
			date.setDate(date.getDate());
			$("input[name=start_date]").val([date.getDate(), date.getMonth() + 1, date.getFullYear()].join("/"));
			$("input[name=end_date]").val([date.getDate(), date.getMonth() + 1, date.getFullYear()].join("/"));
			datePicker.datepicker( "refresh" );
		});

		//select yesterday range dates
		$("a[href=#yesterday-link]").bind("click", function(e){
			e.preventDefault();
			minD = null;
			var date = new Date();
			date.setDate(date.getDate() -1);
			$("input[name=start_date]").val([date.getDate(), date.getMonth() + 1, date.getFullYear()].join("/"));
			$("input[name=end_date]").val([date.getDate(), date.getMonth() + 1, date.getFullYear()].join("/"));
			datePicker.datepicker( "refresh" );
		});

		//select last week range dates
		$("a[href=#lastweek-link]").bind("click", function(e){
			e.preventDefault();
			minD = null;
			//get previous saturday date
			var date = new Date();
			date.setDate(date.getDate());
			date.setUTCDate(date.getUTCDate() - ((date.getUTCDay()) % 7));
			date.setUTCSeconds(0);
			date.setUTCMinutes(0);
        	date.setUTCHours(0);
        	$("input[name=end_date]").val([date.getDate(), date.getMonth() + 1, date.getFullYear()].join("/"));

        	//get 6 days past the previous satruday date
        	var i = date.getTime() - 6 * 24 * 60 * 60 * 1000
        	date = new Date(i);
			$("input[name=start_date]").val([date.getDate(), date.getMonth() + 1, date.getFullYear()].join("/"));

			datePicker.datepicker( "refresh" );
		});

		//select last month range dates
		$("a[href=#lastmonth-link]").bind("click", function(e){
			e.preventDefault();
			minD = null;
			//get previous saturday date
			var date = new Date();
			var firstDay = new Date(date.getFullYear(), date.getMonth() - 1, 1);
			var lastDay = new Date(date.getFullYear(), date.getMonth(), 0);

			$("input[name=start_date]").val([firstDay.getDate(), firstDay.getMonth() + 1, firstDay.getFullYear()].join("/"));
			$("input[name=end_date]").val([lastDay.getDate(), lastDay.getMonth() + 1, lastDay.getFullYear()].join("/"));

			datePicker.datepicker( "refresh" );
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
		this.trigger('timeseriesform:submited');
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