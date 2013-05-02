// js/views/list/list.js

var app = app || {};

app.ListView = Backbone.View.extend({
	className: 'list-side-content',

	template: _.template($("#list-template").html()),

	collection: null,

	selectedItem: null,

	events: {
		'click a': 'selectItem'
	},

	initialize: function() {
		this.collection = this.options.collection;
		this.collection = new this.collection();
		this.collection.on('sync', this.render, this);
		this.collection.fetch();
	},

	serialize: function() {
		return {
			collection: this.collection.toJSON()
		}
	},

	render: function() {
		this.$el.html(this.template(this.serialize()));
		return this;
	},

	selectItem: function(e) {
		e.preventDefault();
		this.$el.children().children().removeClass('active');
		$(e.currentTarget).parent().addClass('active');

		this.selectedItem = this.collection.get($(e.currentTarget).attr('resource_uri'));

		app.appRouter.navigate($(e.currentTarget).attr('href'), {trigger: true});
	},

	onClose: function() {
		this.stopListening(this.collection);
	},

});