// js/views/navtabs/accounts/shopnavtabcontent.js

var app = app || {};


app.ShopNavTabContentView = app.AccountsNavTabContentView.extend({

	template: _.template($("#shopnavtabcontent-template").html()),

	model: app.ShopModel,

	serializeDataObject: function() {
		var data = this.$el.children('form').serializeObject();

		var object = {
				about: data.about,
				default_address: {	
					address1: data.address1,
					city: data.city,
					zipcode: data.zipcode,
					patron: this.model.toJSON().resource_uri,
				},
				default_number: {
					number: data.number,
					patron: this.model.toJSON().resource_uri,
				},
				company_name: data.company_name,
				url: data.url
			};

		if ( !_.isNull(shop.toJSON().default_address) ) object.default_address.id = shop.toJSON().default_address.id;
		if ( !_.isNull(shop.toJSON().default_number) ) object.default_number.id = shop.toJSON().default_number.id;

		return object;
	}
});