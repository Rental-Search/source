// js/views/navtabs/accounts/billingnavtabcontent.js

var app = app || {};


app.BillingNavTabContentView = app.NavTabContentView.extend({

	template: _.template($("#billingnavtabcontent-template").html()),

	initialize: function() {
		if (this.options.titleName) this.titleName = this.options.titleName;

		this.render();
	},

	serialize: function() {
		return {
			titleName: this.titleName
		}
	},

	render: function() {
		this.$el.html(this.template(this.serialize()));
		return this;
	}
});