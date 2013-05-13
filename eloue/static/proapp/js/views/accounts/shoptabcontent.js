// js/views/accounts/shoptabcontent.js

var app = app || {};

app.ShopTabContentView = app.AccountsTabContentView.extend({
	
	titleName: 'L\'agence',

	item: app.NavTabItemView.extend({
		template: _.template($("#navtabsitem-template").html()),
		icon: 'home', 
		path: 'accounts/shop/', 
		labelName: 'L\'agence'
	}),
	
	model: app.ShopModel,

	template: _.template($("#shopnavtabcontent-template").html()),

	events: {
		'submit form':				'submitForm',
		'click button.cancel':		'cancelForm',
		'click a.open-slot': 		'openSlot',
		'click a.close-slot':  		'closeSlot',
		'click a.clone-slot': 		'cloneSlot'
	},

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
				url: data.url,
				opening_times: {
					monday_opens: data.monday_opens || null,
					monday_closes: data.monday_closes || null,
					monday_opens_second: data.monday_opens_second || null,
					monday_closes_second: data.monday_closes_second || null,
					tuesday_opens: data.tuesday_opens || null,
					tuesday_closes: data.tuesday_closes || null,
					tuesday_opens_second: data.tuesday_opens_second || null,
					tuesday_closes_second: data.tuesday_closes_second || null,
					wednesday_opens: data.wednesday_opens || null,
					wednesday_closes: data.wednesday_closes || null,
					wednesday_opens_second: data.wednesday_opens_second || null,
					wednesday_closes_second: data.wednesday_closes_second || null,
					thursday_opens: data.thursday_opens || null,
					thursday_closes: data.thursday_closes || null,
					thursday_opens_second: data.thursday_opens_second || null,
					thursday_closes_second: data.thursday_closes_second || null,
					friday_opens: data.friday_opens || null,
					friday_closes: data.friday_closes || null,
					friday_opens_second: data.friday_opens_second || null,
					friday_closes_second: data.friday_closes_second || null,
					saturday_opens: data.saturday_opens || null,
					saturday_closes: data.saturday_closes || null,
					saturday_opens_second: data.saturday_opens_second || null,
					saturday_closes_second: data.saturday_closes_second || null,
					sunday_opens: data.sunday_opens || null,
					sunday_closes: data.sunday_closes || null,
					sunday_opens_second: data.sunday_opens_second || null,
					sunday_closes_second: data.sunday_closes_second || null,
					patron: this.model.toJSON().resource_uri,
				}
			};

		if ( !_.isNull(shop.toJSON().default_address) ) object.default_address.id = shop.toJSON().default_address.id;
		if ( !_.isNull(shop.toJSON().default_number) ) object.default_number.id = shop.toJSON().default_number.id;
		if ( !_.isNull(shop.toJSON().opening_times.id) ) object.opening_times.id = shop.toJSON().opening_times.id;

		return object;
	},

	afterRender: function() {
		_.each(this.$('table.table-time table tr'), function(opening_times) {
			_.each($(opening_times).children('td'), function(time) {
				var open_time = ($(time).children('div.input-append')[0]);
				var close_time = ($(time).children('div.input-append')[1]);

				if ( !_.isEmpty($(open_time).children('input').val()) &&  !_.isEmpty($(close_time).children('input').val()) ) $(opening_times).show();
			});
		});
	},

	openSlot: function(e) {
		e.preventDefault();
		slots = this._getSlots(e.currentTarget);
     	this._showSlot(slots);
	},

	closeSlot: function(e) {
		e.preventDefault();
		slots = this._getSlots(e.currentTarget);
		this._hideSlot(slots);
	},

	cloneSlot: function(e) {
		e.preventDefault();
		var slots = this._getSlots(e.currentTarget),
			previousSlots = this._getPreviousSlot(e.currentTarget),
			times = this._getTimeValue(previousSlots);

		this._setTimeValue(slots, times);
	},	

	_getSlots: function(clickedElement) {
		return $(clickedElement).parent().parent().parent().parent().children('.times-range').children('table').children('tbody').children('tr');
	},

	_getPreviousSlot: function(clickedElement) {
		return $(clickedElement).parent().parent().parent().parent().prev().children('.times-range').children('table').children('tbody').children('tr');
	},

	_showSlot: function(slots) {
		if (slots.first().is(":visible") == false) slots.first().show();
      	else slots.last().show();
	},

	_hideSlot: function(slots) {
		if (!slots.last().is(":visible")) {
			slots.first().hide()
			_.each($(slots.first()).children('td').children('div.input-append').children('input'), function(input) {
				$(input).val('');
			});
		} else {
			slots.last().hide();
			_.each($(slots.last()).children('td').children('div.input-append').children('input'), function(input) {
				$(input).val('');
			});
	    }

	    /*_.each(slots, function(slot) {
	    	$(slot).children('td').children('div.input-append').children('input').val("");
	    });*/
	},

	_getTimeValue: function(slots) {
		var times = [];
		_.each(slots, function(slot) {
	    	_.each($(slot).children('td').children('div.input-append').children('input'), function(input) {
	    		times.push($(input).val());
	    	});
	    });
	    return times
	},

	_setTimeValue: function(slots, times) {
		var inputTimer = []
		_.each(slots, function(slot) {
			_.each($(slot).children('td').children('div.input-append').children('input'), function(input) {
				inputTimer.push(input);
			});
		});
		_.each(times, function(time, index) {
			var input = $(inputTimer[index]);
			input.val(time);
			if( !_.isEmpty(time) && !$(input).is(":visible") ) input.parent().parent().parent().show();
		});
	}
});