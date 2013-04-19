// js/collections/plan.js

var app = app || {};

app.PlansCollection = Backbone.Collection.extend({

	model: app.PlanModel,

	url: API_URL.plan

});