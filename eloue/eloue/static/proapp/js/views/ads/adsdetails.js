// js/views/ads/adsdetails.js

var app = app || {};

app.AdsDetailsView = app.NavView.extend({
	className: 'list-main-content',

	model: null,

	template: _.template($("#ads-details-template").html()),

	initialize: function() {
		this.navTabItemsView = this.navTabItemsView.extend({ id: 'product-nav', className: 'nav'})
		
		this.navTabViews =  [app.AdsInfoView, app.AdsPicView, app.AdsPriceView];
	},

	setModel: function(model) {
		this.model = model;
		this.navTabViews[0].prototype.item.prototype.path = 'ads/' + this.model.id + '/';
		this.navTabViews[1].prototype.item.prototype.path = 'ads/' + this.model.id + '/pictures/';
		this.navTabViews[2].prototype.item.prototype.path = 'ads/' + this.model.id + '/prices/';
	},

	serialize: function() {
		if( _.isNull(this.model) ) return { model: this.model }
		else return { model: this.model.toJSON() }
	},

	render: function() {
		this.$el.html(this.template(this.serialize()));
		if ( !_.isNull(this.model) ) this.renderNavTabItems();
		return this;
	},

	renderNavTabItems: function() {
		this.setItems();
		this.$el.children('.navbar').children('.navbar-inner').append(this.navTabItemsView.$el);
		this.navTabItemsView.render();
	},

	renderSelectedNavTabView: function() {
		this.$el.append(this.selectedNavTabView.$el);
		this.selectedNavTabView.render();
		this.selectedNavTabView.setModel(this.model);
	},
});