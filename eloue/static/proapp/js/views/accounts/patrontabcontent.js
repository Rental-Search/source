// js/views/accounts/patrontabcontent.js

var app = app || {};

app.PatronTabContentView = app.AccountsTabContentView.extend({
	
	titleName: 'Le gérant',

	item: app.NavTabItemView.extend({
		template: _.template($("#navtabsitem-template").html()),
		icon: 'user', 
		path: 'accounts/', 
		labelName: 'Le gérant'
	}),
	
	model: app.PatronModel,

	template: _.template($("#accountsnavtabcontent-template").html()),
});