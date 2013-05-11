// js/views/layout.js

var app = app || {};

app.LayoutView = app.NavView.extend({
	id: 'pro-app',

	className: 'container-fluid',

	initialize: function() {
		//Extend the class name for navpills
		this.navTabItemsView = this.navTabItemsView.extend({className:  'nav nav-pills  top-nav'});

		var itemView = app.NavTabItemView.extend({
			template: _.template($("#navpillsitem-template").html()),
		});

		var HomeView = Backbone.View.extend({
			className: 'content-pill',

			item: itemView.extend({path: '', icon: 'home', labelName: 'Acceuil'}),

			render: function() {
				this.$el.html('<h1>Acceuil</h1>');
				return this;
			},
		});

		var StatsView = Backbone.View.extend({
			className: 'content-pill',

			item: itemView.extend({path: 'stats/', icon: 'stats', labelName: 'Statistiques'}),

			render: function() {
				this.$el.html('<h1>Statistique</h1>');
				return this;
			},
		});

		var MessagesView = Backbone.View.extend({
			className: 'content-pill',

			item: itemView.extend({path: 'messages/', icon: 'envelope', labelName: 'Messages'}),

			render: function() {
				this.$el.html('<h1>Messages</h1>');
				return this;
			},
		});

		var AdsView = Backbone.View.extend({
			className: 'content-pill',

			item: itemView.extend({path: 'ads/', icon: 'show_thumbnails_with_lines', labelName: 'Annonces'}),

			render: function() {
				this.$el.html('<h1>Annonces</h1>');
				return this;
			},
		});

		var AccountsView = Backbone.View.extend({
			className: 'content-pill',

			item: itemView.extend({path: 'accounts/', icon: 'nameplate', labelName: 'Compte'}),

			render: function() {
				this.$el.html('<h1>Compte</h1>');
				return this;
			},
		});
		
		this.navTabViews = [HomeView, StatsView, MessagesView, AdsView, AccountsView];
	},
});