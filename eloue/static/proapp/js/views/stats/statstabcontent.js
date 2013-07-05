// js/views/navtabs/stats/statstabcontent.js

var app = app || {};

app.StatsTabContentView = Backbone.View.extend({
	className: 'tab-content',

	item: null,

	titleName: '',

	chartItem: {
		model: null,
		chartsLegendItem: {
			className: null, 
			icon: null, 
			labelName: null, 
			count: null	
		},
		dataset: {
			data: null,
      		color: null,
      		label: null
		},
		interval: null,
		headerItems: []
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
		this.chartItem.model.on('sync', this.renderStats, this);

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
			.success(function() {
				self.timeSeries = self._getTimeSeries();
				self.trigger('timeSeries:change');
			})
			.fail(function() {
				self.renderFail();
			});
		delete params;
		delete self;
	},

	serialize: function() {
		this.chartItem.chartsLegendItem.count = this.chartItem.model.toJSON().count;
		this.chartItem.dataset.data = this.chartItem.model.toJSON().data;
		this.chartView.interval = this.chartItem.model.toJSON().interval;
	},

	render: function() {
		return this;
	},

	renderStats: function() {
		this.$el.html("<h3>" + this.titleName + "</h3>");

		if (this.timeSeriesView) {
			this.$el.children("h3").append(this.timeSeriesView.$el);
			this.timeSeriesView.render(this._getTimeSeries());
		}

		this.serialize();

		this.renderCharts();
		this.renderChartsDetails();
	},

	renderCharts: function() {
		this.$el.append(this.chartView.$el);
		this.chartView.chartsLegendItems = [this.chartItem.chartsLegendItem]
		this.chartView.datasets = [this.chartItem.dataset];
		this.chartView.render();
	},

	renderChartsDetails: function() {
		this.chartsDetailsView.headerItems = this.chartItem.headerItems;
		this.chartsDetailsView.dataList = this.serializeChartsDetails();
		this.$el.append(this.chartsDetailsView.$el);
		this.chartsDetailsView.render();
	},

	renderFail: function() {
		this.$el.html("<h3>" + this.titleName + "</h3>");
		this.$el.append("<p>Impossible de récupérer les données.</p>");
	},

	serializeChartsDetails: function() {
		return _.countBy(this.chartItem.model.toJSON().details, function(line) { return line[3]; });
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