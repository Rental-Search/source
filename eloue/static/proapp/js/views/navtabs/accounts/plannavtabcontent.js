// js/views/navtabs/accounts/plannavtabcontent.js

var app = app || {};


app.PlanNavTabContentView = app.AccountsNavTabContentView.extend({

	template: _.template($("#plannavtabcontent-template").html()),

	model: app.PlansCollection,

	events: {
		'submit form':				'submitForm',
	},

	submitForm: function (e) {
		var data = this.serializeDataObject(e.currentTarget);

		var subscriptionModel = new app.SubscriptionModel();

		var self = this;
		
		subscriptionModel.fetch({
			success: function(model, response, options) {
				subscriptionModel.save(data, {
					success: function(model, response, options) {
						self.model.fetch();
					},
					error: function(model, xhr, options) {
						console.log("error to save");
					}
				});
			},
			error: function(model, xhr, options) {
				console.log("error to fetch");
			}
		});

		console.log(subscriptionModel.toJSON());

		var self = this;

		return false;
	},

	serializeDataObject: function(form) {
		var data = $(form).serializeObject();
		var object = {
			propackage: {
				id: data.subscription
			}
		}
		return object
	},
});