// js/views/navtabs/accounts/plannavtabcontent.js

var app = app || {};


app.SubscriptionNavTabContentView = app.AccountsNavTabContentView.extend({

	template: _.template($("#plannavtabcontent-template").html()),

	model: app.SubscriptionModel,

	events: {
		'submit form':				'submitForm',
	},

	submitForm: function (e) {
		var data = this.serializeDataObject(e.currentTarget);

		console.log(data);

		this.model.save(data, {
			success: function(model, response, options) {
				console.log(model);
				console.log(response);
				console.log(options);
			},
			error: function(model, xhr, options) {
				console.log(model);
				console.log(xhr);
				console.log(options);
			}
		});

		return false;
	},

	serializeDataObject: function(form) {
		var data = $(form).serializeObject();
		console.log(data.subscription)
		var object = {
			propackage: {
				id: data.subscription
			}
		}
		return object
	},
});