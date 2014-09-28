// js/views/accounts/plantabcontent.js

var app = app || {};

app.PlanTabContentView = app.AccountsTabContentView.extend({
	
	titleName: 'Facturation',

	item: app.NavTabItemView.extend({
		template: _.template($("#navtabsitem-template").html()),
		icon: 'list-alt', 
		path:'accounts/plan/', 
		labelName: 'Abonnements'
	}),
	
	model: app.PlansCollection,

	template: _.template($("#plannavtabcontent-template").html()),

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