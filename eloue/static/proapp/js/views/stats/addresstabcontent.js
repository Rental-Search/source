// js/views/stats/addresstabcontent.js

var app = app || {};


app.AddressTabContentView = app.StatsTabContentView.extend({

	item: app.NavTabItemView.extend({
		template: _.template($("#navtabsitem-template").html()),
		icon: 'map-marker', 
		path: 'stats/address/', 
		labelName: 'Adresses'
	}),

	titleName: 'Adresses',

	chartItem: {
		model: new app.AddressEventModel(),
		chartsLegendItem: {
			className: 'charts-addresses', 
			icon: 'map-marker', 
			labelName: 'Adresse', 
			count: null	
		},
		dataset: {
			data: null,
      		color: "#349B9D",
      		label: "Adresses"
		},
		interval: null,
		headerItems: ['Pages', 'Nombre de vue']
	}
		
});