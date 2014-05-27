// js/views/navtabs/accounts/patronnavtabcontent.js

var app = app || {};


app.PatronNavTabContentView = app.AccountsNavTabContentView.extend({

	template: _.template($("#accountsnavtabcontent-template").html()),

	model: app.PatronModel

});