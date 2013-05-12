// js/views/navtabs/stats/trafficnavtabcontent.js

var app = app || {};


app.TrafficTabContentView = app.StatsTabContentView.extend({

	item: app.NavTabItemView.extend({
		template: _.template($("#navtabsitem-template").html()),
		icon: 'user', 
		path: 'stats/', 
		labelName: 'Visites'
	}),

	titleName: 'Visites',

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