// js/views/navtabs/navtabcontent.js

var app = app || {}

app.NavTabContentView = Backbone.View.extend({
	className: 'tab-content',

	titleName: '',

	timeSeriesView: null,

	timeSeries: null,

	initialize: function() {
		if (this.options.titleName) this.titleName = this.options.titleName;

		this.render();
	},

	setTimeSeriesView: function(timeSeriesView) {
		this.timeSeriesView = timeSeriesView;
		//this.timeSeriesView.on('timeseriesform:submited', this.render, this);
	},

	render: function() {
		this.$el.html("<h3>" + this.titleName + "</h3>");
		if (this.timeSeriesView) {
			this.$el.children("h3").append(this.timeSeriesView.$el);
			this.timeSeriesView.render();
		}
		return this;
	}
});