// js/models/redirection.js

var app = app || {};

app.RedirectionEventModel = Backbone.Model.extend({
	
	urlRoot: API_URL.redirection_events + "analytics/",

	validate: function(attrs, options) {
		if(!attrs.start_date) {
			return 'invalid date';
		}
	}
});