// js/views/navtabs/stats/redirectionnavtabcontent.js

var app = app || {};


app.RedirectionNavTabContentView = app.NavTabContentView.extend({

	chartItem: {
		model: new app.RedirectionEventModel(),
		chartsLegendItem: {
			className: 'charts-redirections', 
			icon: 'link', 
			labelName: 'Redirection', 
			count: null	
		},
		dataset: {
			data: null,
      		color: "#fe8f00",
      		label: "Redirections"
		},
		interval: null,
		headerItems: ['Pages', 'Nombre de redirections']
	},

	initialize: function() {
		if (this.options.titleName) this.titleName = this.options.titleName;
		this.loadingView = new app.LoadingView();
		
		this.chartView = new app.ChartsView();
		this.chartView.on('interval:change', this.fetchModel, this);

		this.chartsDetailsView = new app.ChartsDeatilsView();
	},

	setTimeSeriesView: function(timeSeries) {
		this.timeSeries = timeSeries;
		this.timeSeriesView = new app.TimeSeriesView();
		this.timeSeriesView.on('timeseriesform:submited', this.fetchModel, this);
		
		this.chartItem.model.on('request', this.renderLoading, this);
		this.chartItem.model.on('sync', this.render, this);

		this.fetchModel();
	},

	fetchModel: function() {
		var self = this;
		var params;

		if(self.timeSeriesView.serializeForm()) {
			params = self.timeSeriesView.serializeForm();
		} else if (self.timeSeries) {
			params = $.param(self.timeSeries);
		} else {
			params = null;
		}

		this.chartItem.model.fetch({data: params})
			.success(function () {
				self.timeSeries = self._getTimeSeries();
				self.trigger('timeSeries:change');
			});

		delete params;
		delete self;
	},

	render: function() {
		//app.redirectionModel = this.model.toJSON();
		this.$el.html("<h3>" + this.titleName + "</h3>");

		if (this.timeSeriesView) {
			this.$el.children("h3").append(this.timeSeriesView.$el);
			this.timeSeriesView.render(this._getTimeSeries());
		}

		this.renderCharts();
		this.renderChartsDetails();

		return this;
	},

	renderCharts: function() {
		this.$el.append(this.chartView.$el);

		this.chartItem.chartsLegendItem.count = this.chartItem.model.toJSON().count;
		this.chartView.chartsLegendItems = [this.chartItem.chartsLegendItem]
		
		this.chartItem.dataset.data = this.chartItem.model.toJSON().data;
		this.chartView.datasets = [this.chartItem.dataset];

        this.chartView.interval = this.chartItem.model.toJSON().interval;

		this.chartView.render();

		delete chartsLegendItems;
		delete datasets;
	},

	renderChartsDetails: function() {
		this.chartsDetailsView.headerItems = this.chartItem.headerItems;
		this.chartsDetailsView.dataList = _.countBy(this.chartItem.model.toJSON().details, function(redirection) { return redirection[3]; });
		this.$el.append(this.chartsDetailsView.$el);
		this.chartsDetailsView.render();
	},

	renderLoading: function() {
		this.$el.html(this.loadingView.$el);
		this.loadingView.render();
	},

	_getTimeSeries: function() {
		return {
			start_date: String(this.chartItem.model.get('start_date')), 
			end_date: String(this.chartItem.model.get('end_date')), 
			interval: String(this.chartItem.model.get('interval'))
		};
	},

	onClose: function() {
		this.timeSeriesView.close();
		this.loadingView.close();
		this.chartView.close();
		this.chartsDetailsView.close();
		this.chartItem.model.unbind();
		delete this.chartItem;
	}
});