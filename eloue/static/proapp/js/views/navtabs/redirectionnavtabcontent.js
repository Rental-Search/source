// js/views/navtabs/stats/redirectionnavtabcontent.js

var app = app || {};

app.RedirectionNavTabContentView = app.NavTabContentView.extend({

	initialize: function() {
		this.timeSeriesForm = new app.TimeSeriesForm();
	},

	render: function() {
		console.log("redirection render");
		this.$el.html("<h3>" + this.titleName + "<h3>");
		this.$el.height(400);
		console.log(this.$el.children("h3"));
		this.$el.children("h3").append(this.timeSeriesForm.$el);
		this.timeSeriesForm.render();
		return this;
	}

});