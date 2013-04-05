// js/views/navtabs/accounts/shopnavtabcontent.js

var app = app || {};


app.ShopNavTabContentView = app.AccountsNavTabContentView.extend({

	template: _.template($("#shopnavtabcontent-template").html()),

	model: app.ShopModel,

	serializeDataObject: function() {
		data = this.$el.children('form').serializeObject();

		return {
			about: data.about,
			addresses: [
				{	
					address1: data.address1,
					city: data.city,
					zipcode: data.zipcode,
				}
			],
			phones: [
				{
					number: data.number,
				}
			],
			company_name: data.company_name,
			url: data.url
		};
	}
});