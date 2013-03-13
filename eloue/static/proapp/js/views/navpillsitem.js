// js/views/navpillsitem.js

var app = app || {};


app.NavPillsItem = Backbone.View.extend({
	tagName: 'li',
	
	icon: '',
	
	labelName: '',

	template: _.template($("#napillsitem-template").html()),

	initialize: function (){

	},

	render: function() {
		this.$el.html(this.template({'icon': this.icon, 'label': this.labelName}));
	}
});