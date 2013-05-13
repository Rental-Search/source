// js/views/accounts/accountstabcontent.js

var app = app || {};

app.AccountsTabContentView = Backbone.View.extend({
	className: 'tab-content',

	item: null,

	titleName: '',

	model: null,

	template: null,

	initialize: function() {
		this.loadingView = new app.LoadingView();

		this.model = new this.model();
		this.model.on('request', this.renderLoading, this);
		this.model.on('sync', this.render, this);
		this.model.on('invalid', this.showErrors, this);
		this.model.fetch();

		this.on('accounttabcontentrender:after', this.renderAfter, this);
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
		this.trigger('accounttabcontentrender:after');
		return this;
	},

	renderLoading: function() {
		this.$el.html(this.loadingView.$el);
		this.loadingView.render();
	},

	renderAfter: function() {},

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