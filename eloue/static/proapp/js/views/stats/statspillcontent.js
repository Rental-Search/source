// js/view/stats/statspillcontent.js

var app = app || {};

app.StatsPillContentView = app.NavView.extend({
	
	id: 'content-stats',

	className: 'content-pill tabbable tabs-left',

	item: app.NavTabItemView.extend({
		template: _.template($("#navpillsitem-template").html()),

		path: 'stats/',

		icon: 'stats',

		labelName: 'Statistiques'
	}),

	timeSeries: null,

	initialize: function() {	
		//Extend the class name for navtabs
		this.navTabItemsView = this.navTabItemsView.extend({className:  'nav nav-tabs border-right'});

		this.navTabViews = [app.TrafficTabContentView, app.RedirectionTabContentView, app.PhoneTabContentView, app.AddressTabContentView];

		this.on('selectedNavTabView:change', this.selectedNavTabViewChange, this);
	},

	selectedNavTabViewChange: function() {
		this.selectedNavTabView.on('timeSeries:change', this.updateTimeSeries, this);
		this.selectedNavTabView.setTimeSeriesView(this.timeSeries);
	},

	updateTimeSeries: function () {
		this.timeSeries = this.selectedNavTabView.timeSeries;
	},
});