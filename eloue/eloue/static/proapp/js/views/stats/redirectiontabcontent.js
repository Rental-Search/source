// js/views/stats/redirectiontabcontent.js

var app = app || {};


app.RedirectionTabContentView = app.StatsTabContentView.extend({

	item: app.NavTabItemView.extend({
		template: _.template($("#navtabsitem-template").html()),
		icon: 'link', 
		path: 'stats/redirection/', 
		labelName: 'Redirections'
	}),

	titleName: 'Redirections',

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
	}
		
});