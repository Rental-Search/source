// js/views/navtabs/stats/phonenavtabcontent.js

var app = app || {};


app.PhoneNavTabContentView = app.StatsNavTabContentView.extend({

	chartItem: {
		model: new app.PhoneEventModel(),
		chartsLegendItem: {
			className: 'charts-calls', 
			icon: 'phone', 
			labelName: 'Appel', 
			count: null	
		},
		dataset: {
			data: null,
      		color: "#9dcc09",
      		label: "Phones"
		},
		interval: null,
		headerItems: ['Pages', 'Nombre d\'appels']
	}
		
});