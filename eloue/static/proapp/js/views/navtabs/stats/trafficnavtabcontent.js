// js/views/navtabs/stats/trafficnavtabcontent.js

var app = app || {};


app.TrafficNavTabContentView = app.StatsNavTabContentView.extend({

	chartItem: {
		model: new app.TrafficEventModel(),
		chartsLegendItem: {
			className: 'charts-traffic', 
			icon: 'user',
			labelName: 'Visite', 
			count: null	
		},
		dataset: {
			data: null,
      		color: "#fe8f00",
      		label: "Vsites"
		},
		interval: null,
		headerItems: ['Pages', 'Nombre de visites']
	},

	serializeChartsDetails: function() {
		return _.countBy(this.chartItem.model.toJSON().details, function(line) { return line[1]; });
	},
		
});