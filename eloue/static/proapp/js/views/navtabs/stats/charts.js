// js/views/navtabs/stats/charts.js

var app = app || {};


app.ChartsView = Backbone.View.extend({
	className: 'charts',

	template: _.template($("#charts-template").html()),

    toolTipTemplate: _.template($("#chartstooltip-template").html()),

	datasets: null,

    plot: null,

    chartsLegendItems: null,

    interval: null,

    monthList: ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juill.", "août", "sept.", "oct.", "nov.", "déc."],

    dayList: ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"],

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
        var self = this;
        
        _.each(this.datasets, function(data) {
            if (_.size(data.data) > 0) {
                if (self.interval == 'weeks') {
                    data.data = self._newWeeksDataArray(data.data);
                } else if (self.interval == 'months') {
                    data.data = self._newMonthsDataArray(data.data);
                } else {
                    data.data = self._newDaysDataArray(data.data);
                }
            }
        });

        var flotOptions = {
            xaxis: { color: "#364c59", mode: "time", timeformat: "%d %b", monthNames: this.monthList, autoscaleMargin: 0},
            yaxis: { color: "#364c59", tickDecimals: 0, min: 0, position: 'left', transform: function (v) { return v; }},
            selection: { mode: "x" },
            grid: { markings: this._weekendAreas, borderColor: "#364c59", borderWidth: 0, hoverable: true},
            series: { lines: { show: true }, points: { show: true } },
            legend: { show: true }
        };

        this.plot = $.plot(this.$el.children("#overview").children('#plot'), this.datasets, flotOptions);
        $("#plot").bind("plothover", this, this.toolTip);
        
        $(window).resize(function () {
          self.plot.resize();
          self.plot.setupGrid();
          self.plot.draw();
        });
        delete self;
	},

    renderTooltip: function(x, y, contents) {
        var d = new Date(contents.datapoint[0]);

        var object = {
            'date': [this.dayList[d.getDay()], d.getDate(), this.monthList[d.getMonth()], d.getFullYear()].join(" "),
            'label': contents.series.label,
            'count': contents.datapoint[1],
            'color': contents.series.color
        }

        $(this.toolTipTemplate(object)).css( {
            top: y - 80,
            left: x - 98,
        }).appendTo("body").fadeIn(200);

        delete d;
        delete object;
    },

    updateInterval: function(e) {
        $("div.filter-time").children().removeClass('active');
        $(e.currentTarget).addClass('active');
        $("form.form-inline").children("input[name=interval]").val($(".filter-time .active").attr('id'));
        this.trigger("interval:change");
    },

    toolTip: function (event, pos, item) {
        self = event.data;
        if (item) {
            if (previousPoint != item.series.label) {
                previousPoint = item.series.label;

                $('#charts-popover').remove();
                self.renderTooltip(item.pageX, item.pageY, item);
            }
        }
        else {
            $("#charts-popover").remove();
            previousPoint = null;            
        }
        delete self;
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
	},

    /* create and return new array padding missing days*/
    _newDaysDataArray: function(data) {
        var startDay = data[0][0],
        newData = [data[0]];

        for (i = 1; i < data.length; i++) {
            var diff = this._dateDayDiff(data[i - 1][0], data[i][0]);
            var startDate = new Date(data[i - 1][0]);
            if (diff > 1) {
                for (j = 0; j < diff - 1; j++) {
                    var fillDate = new Date(startDate).setDate(startDate.getDate() + (j + 1));
                    newData.push([fillDate, 0]);
                }
            }
            newData.push(data[i]);
        }
        return newData;
    },

    /* create and return new array padding missing weeks*/
    _newWeeksDataArray: function(data) {
        var newData = [data[0]];
        
        for (i = 1; i < data.length; i++) {
            var diff = this._dateWeekDiff(data[i - 1][0], data[i][0]);
            if (diff > 1) {
                var startDate = new Date(data[i - 1][0]);
                startDate.setUTCDate(startDate.getUTCDate() - ((startDate.getUTCDay()) % 7))
                for(j = 0; j <= diff - 1; j++) {
                    startDate = new Date(startDate.getTime() + 7 * 24 * 60 * 60 * 1000);
                    newData.push([startDate, 0]);
                }
            }
            newData.push(data[i]);
        }
        return newData;
    },

    /* create and return new array padding missing months*/
    _newMonthsDataArray: function(data) {
        var newData = [data[0]];
        for (i = 1; i < data.length; i++) {
            var diff = this._dateMonthDiff(data[i - 1][0], data[i][0]);
            if (diff > 1) {
                var startDate = new Date(data[i - 1][0]);
                for(j = 0; j <= diff - 1; j++) {
                    startDate = new Date(startDate.getFullYear(), startDate.getMonth()+1, 01);
                    newData.push([startDate, 0]);
                }
            }
            newData.push(data[i]);
        }
        return newData;
    },

    /* helper functions to find date differences*/
    _dateDayDiff: function(d1, d2) {
        return Math.floor((d2 - d1) / (1000 * 60 * 60 * 24));
    },

    _dateWeekDiff: function(d1, d2) {
        return Math.floor((d2 - d1) / (7 * 24 * 60 * 60 * 1000));
    },

    _dateMonthDiff: function(d1, d2) {
        d1 = new Date(d1);
        d2 = new Date(d2);
        var months;
        months = (d2.getFullYear() - d1.getFullYear()) * 12;
        months -= d1.getMonth() + 1;
        months += d2.getMonth();
        return months <= 0 ? 0 : months;
    }
});