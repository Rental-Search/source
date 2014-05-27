// js/views/navtabs/accounts/accountsnavtabcontent.js

var app = app || {};


app.AccountsNavTabContentView = app.NavTabContentView.extend({

	template: null,

	model: null,

	events: {
		'submit form':				'submitForm',
		'click button.cancel':		'cancelForm'
	},

	initialize: function() {
		if (this.options.titleName) this.titleName = this.options.titleName;

		this.loadingView = new app.LoadingView();

		this.model = new this.model();
		this.model.on('sync', this.render, this);
		this.model.on('invalid', this.showErrors, this);

		this.renderLoading();
		this.model.fetch();
	},

	serialize: function() {
		return {
			titleName: this.titleName,
			model: this.model.toJSON()
		}
	},

	serializeDataObject: function() {
		return this.$el.children('form').serializeObject();
	},	

	render: function() {
		this.$el.html(this.template(this.serialize()));
		this.afterRender();
		return this;
	},

	renderLoading: function() {
		this.$el.html(this.loadingView.$el);
		this.loadingView.render();
	},

	afterRender: function() {},

	submitForm: function () {
		var data = this.serializeDataObject();

		this._disabledForm();

		var self = this;
		this.model.save(data, {
			success: function(model, response, options) {
				self._enabledForm();
			},
			error: function(model, xhr, options) {
				console.log("Erreur lors de la mise à jour de vos informations");
				console.log(xhr);
				self._enabledForm();
			}
		});

		return false;
	},

	cancelForm: function () {
		this.model.fetch();
	},

	showErrors: function() {
		//reset errors messages
		this.$('.error').children('.help-inline').remove();

		//display errors for each field
		_.each(this.model.validationError, function(error) {
			var field = this.$('[name=' + error.name + ']');
			if ( field.parent().hasClass('control-group') ) {
				field.parent().addClass('error');
				field.after('<span class="help-inline">' + error.msg + '</span>');
			} 
		});

		//enable fields to modify it
		this._enabledForm();
	},

	onClose: function() {
		this.loadingView.close();
		this.model.unbind();
	},

	_disabledForm: function() {
		$('form select, form input, form textarea, form button').prop('disabled', true);
	},

	_enabledForm: function() {
		$('form select, form input, form textarea, form button').prop('disabled', false);
	}

});