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

		//Setup the correct template for the nav tab
		var itemView = app.NavTabItemView.extend({
			template: _.template($("#navtabsitem-template").html()),
		});

		var TrafficView = app.TrafficTabContentView;

		var RedirectionView = app.StatsTabContentView.extend({

			item: itemView.extend({icon: 'link', path: 'stats/redirection/', labelName: 'Redirections'}),

			titleName: 'Redirections',
		});

		var PhoneView = app.StatsTabContentView.extend({

			item: itemView.extend({icon: 'phone', path: 'stats/phone/', labelName: 'Appels'}),

			titleName: 'Téléphones',
		});

		var AddressView = app.StatsTabContentView.extend({

			item: itemView.extend({icon: 'map-marker', path: 'stats/address/', labelName: 'Adresses'}),

			titleName: 'Adresses',
		});

		this.navTabViews = [TrafficView, RedirectionView, PhoneView, AddressView];

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