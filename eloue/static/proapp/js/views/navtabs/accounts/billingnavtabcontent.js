// js/views/navtabs/accounts/billingnavtabcontent.js

var app = app || {};


app.BillingNavTabContentView = app.AccountsNavTabContentView.extend({

	template: _.template($("#billingnavtabcontent-template").html()),

	model: app.BillModel,

	events: {
		'click table.table-billing table thead tr':		'toggleDetails'
	},

	toggleDetails: function(e) {
		var tbody = $(e.currentTarget).parent().parent().children('tbody');
		if( tbody.length ==1 ){
			if( tbody.is(":visible") == false ){
				tbody.show();
				$(e.currentTarget).children().children('i').attr('class', 'halflings-icon minus-sign blue');
			} else {
				tbody.hide();
				$(e.currentTarget).children().children('i').attr('class', 'halflings-icon plus-sign blue')
			}
		}
	}
});