// js/views/stats/phonetabcontent.js

var app = app || {};


app.PhoneTabContentView = app.StatsTabContentView.extend({

	item: app.NavTabItemView.extend({
		template: _.template($("#navtabsitem-template").html()),
		icon: 'phone', 
		path: 'stats/phone/', 
		labelName: 'Appels'
	}),

	titleName: 'Téléphones',

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
      		label: "Appels"
		},
		interval: null,
		headerItems: ['Pages', 'Nombre d\'appels']
	}
		
});