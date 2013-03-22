// js/views/navtabs/stats/charts.js

var app = app || {};


app.ChartsView = new Backbone.View.extend({
	className: 'charts',

	template: _.template($("#charts-template").html()),

	datasets: null,

	flotOptions: {
        xaxis: { mode: "time", tickLength: 5, color: "#364c59", },
        yaxis: { color: "#364c59", },
        selection: { mode: "x" },
        grid: { markings: this._weekendAreas, borderColor: "#364c59", borderWidth: 1, hoverable: true},
        series: { lines: { show: true }, points: { show: true } },
        legend: { show: true }
    },

    initialize: function() {
    	if (this.options.datasets) this.datasets = this.options.datasets;
    },

    render: function() {
    	this.$el.append(this.template());
    	this.renderPlot();
    	return this;
    },

	renderPlot: function() {
		$.plot(this.$el.children("#overview"), this.datasets, this.flotOptions);
	},

	_weekendAreas: function(axes) {
		var markings = [];
        var d = new Date(axes.xaxis.min);
        // go to the first Saturday
        d.setUTCDate(d.getUTCDate() - ((d.getUTCDay() + 1) % 7))
        d.setUTCSeconds(0);
        d.setUTCMinutes(0);
        d.setUTCHours(0);
        var i = d.getTime();
        do {
            // when we don't set yaxis, the rectangle automatically
            // extends to infinity upwards and downwards
            markings.push({ xaxis: { from: i, to: i + 2 * 24 * 60 * 60 * 1000 }, color: "#ebf2f5" });
            i += 7 * 24 * 60 * 60 * 1000;
        } while (i < axes.xaxis.max);
        return markings;
	}
});