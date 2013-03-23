// js/views/navtabs/stats/charts.js

var app = app || {};


app.ChartsView = Backbone.View.extend({
	className: 'charts',

	template: _.template($("#charts-template").html()),

	datasets: null,

    plot: null,

    chartsLegendItems: null,

    interval: null,

    events: {
        'click .filter-time .btn-mini': 'updateInterval'
    },

    serialize: function() {
        return {
            chartLegends: this.chartsLegendItems
        }
    },

    render: function() {
        this.delegateEvents();
        if (this.plot) {
            this.$el.children("#overview").children().children().remove();
            this.plot = null;
        }
    	this.$el.html(this.template(this.serialize()));
        this.renderFilterTime();
    	this.renderPlot();
    	return this;
    },

    renderFilterTime: function() {
        $("div.filter-time #" + this.interval).addClass('active');
    },

	renderPlot: function() {
        var monthList = ["janv", "févr", "mars", "avr", "mai", "juin", "juill", "août", "sept", "oct", "nov", "déc"]
        var flotOptions = {
            xaxis: { color: "#364c59", mode: "time", timeformat: "%d %b.", monthNames: monthList, autoscaleMargin: 0,},
            yaxis: { color: "#364c59", tickDecimals: 0, min: 0, position: 'left'},
            selection: { mode: "x" },
            grid: { markings: this._weekendAreas, borderColor: "#364c59", borderWidth: 0, hoverable: true},
            series: { lines: { show: true }, points: { show: true } },
            legend: { show: true }
        };

        this.plot = $.plot(this.$el.children("#overview").children('#plot'), this.datasets, flotOptions);

        var self = this;
        $(window).resize(function () {
          self.plot.resize();
          self.plot.setupGrid();
          self.plot.draw();
        });
        delete self;
	},

    updateInterval: function(e) {
        $("div.filter-time").children().removeClass('active');
        $(e.currentTarget).addClass('active');
        $("form.form-inline").children("input[name=interval]").val($(".filter-time .active").attr('id'));
        this.trigger("interval:change");
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