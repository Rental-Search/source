// js/models/redirection.js

var app = app || {};

app.RedirectionEventModel = Backbone.Model.extend({
	urlRoot: API_URL.redirection_events + "analytics/",
});