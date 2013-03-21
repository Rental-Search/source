// js/views/navtabs/stats/redirectionnavtabcontent.js

var app = app || {};

app.RedirectionNavTabContentView = app.NavTabContentView.extend({

	timeSeriesView: null,

	initialize: function() {
		if (this.options.titleName) this.titleName = this.options.titleName;
		this.model = new app.RedirectionEventModel();
		this.model.on('change', this.render, this);
	},

	setTimeSeriesView: function(timeSeriesView) {
		this.timeSeriesView = timeSeriesView;
		this.timeSeriesView.on('timeseriesform:submited', this.fetchModel, this);
		this.fetchModel();
	},

	fetchModel: function() {
		var params = this.timeSeriesView.serializeForm();
		this.model.fetch({data: params});
		delete params;
	},

	render: function() {
		this.$el.html("<h3>" + this.titleName + "</h3>");
		this.$el.height(400);

		if (this.timeSeriesView) {
			this.$el.children("h3").append(this.timeSeriesView.$el);
			this.timeSeriesView.render(this._getTimeSeries());
		}
		return this;
	},

	_getTimeSeries: function() {
		return {
			start_date: String(this.model.get('start_date')), 
			end_date: String(this.model.get('end_date')), 
			interval: String(this.model.get('interval'))
		};
	},

	onClose: function() {
		this.model.unbind();
		delete this.model;
	}
});