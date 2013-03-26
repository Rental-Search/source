// js/views/navtabs/stats/chartsdetails.js

var app = app || {};

app.ChartsDeatilsView = Backbone.View.extend({
	className: 'charts-details',

	template: _.template($("#chartsdetails-template").html()),

	headerItems: null,

	dataList: null,

	serialize: function() {
		return {
			headerItems: this.headerItems,
			dataList: this.dataList
		}
	},

	render: function() {
		var object = this.serialize();
		if (_.size(object.dataList) == 0) {
			this.$el.html("<p style=\"text-align: center;\">Pas de données pour ces dates.</p>")
		} else {
			this.$el.html(this.template(object));
		}
		return this;
	}
});