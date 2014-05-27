// js/views/navtabs/stats/redirectionnavtabcontent.js

var app = app || {};


app.RedirectionNavTabContentView = app.StatsNavTabContentView.extend({

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