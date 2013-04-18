// js/views/navtabs/accounts/plannavtabcontent.js

var app = app || {};


app.SubscriptionNavTabContentView = app.AccountsNavTabContentView.extend({

	template: _.template($("#plannavtabcontent-template").html()),

	model: app.SubscriptionModel,

	events: {
		'submit form':				'submitForm',
	},

	submitForm: function (e) {
		var data = this.serializeDataObject();
		console.log(data);

		return false;
	},

	serializeDataObject: function(form) {
		console.log(form);
		//return this.$el.children('form').serializeObject();
		return true
	},
});