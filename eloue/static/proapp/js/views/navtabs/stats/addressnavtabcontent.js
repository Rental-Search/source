// js/views/navtabs/stats/addressnavtabcontent.js

var app = app || {};


app.AddressNavTabContentView = app.StatsNavTabContentView.extend({

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