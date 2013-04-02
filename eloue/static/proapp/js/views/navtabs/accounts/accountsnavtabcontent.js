// js/views/navtabs/accounts/accountsnavtabcontent.js

var app = app || {};


app.AccountsNavTabContentView = app.NavTabContentView.extend({

	template: _.template($("#accountsnavtabcontent-template").html()),

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