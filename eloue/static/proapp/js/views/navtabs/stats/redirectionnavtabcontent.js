// js/views/navtabs/stats/redirectionnavtabcontent.js

var app = app || {};

app.RedirectionNavTabContentView = app.NavTabContentView.extend({

	timeSeriesView: null,

	initialize: function() {
		if (this.options.titleName) this.titleName = this.options.titleName;
	},

	setTimeSeriesView: function(timeSeriesView) {
		this.timeSeriesView = timeSeriesView;
		this.timeSeriesView.on('timeseriesform:submited', this.render, this);
	},

	render: function() {
		console.log("render redirection view");
		this.$el.html("<h3>" + this.titleName + "</h3>");
		this.$el.height(400);
		if (this.timeSeriesView) {
			this.$el.children("h3").append(this.timeSeriesView.$el);
			this.timeSeriesView.render();
		}
		return this;
	},
});