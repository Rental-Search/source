// js/views/navtabs/stats/redirectionnavtabcontent.js

var app = app || {};

app.RedirectionNavTabContentView = app.NavTabContentView.extend({

	initialize: function() {
		if (this.options.titleName) this.titleName = this.options.titleName;
		this.timeSeriesForm = new app.TimeSeriesForm();
	},

	render: function() {
		this.$el.html("<h3>" + this.titleName + "</h3>");
		this.$el.height(400);
		this.$el.children("h3").append(this.timeSeriesForm.$el);
		this.timeSeriesForm.render();
		return this;
	},

	onClose: function() {
		this.timeSeriesForm.close();
	}
});