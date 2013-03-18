// js/app.js

var app = app || {};


Backbone.View.prototype.close = function(){
  if (this.onClose){
    this.onClose();
  }
  this.remove();
  this.unbind();
}


$(function() {
	console.log("---- App starting ----");
	app.appRouter = new Workspace();
	Backbone.history.start({pushState: true, root: '/pro/dashboard/'})
	$('body').append(app.layoutView.$el);
	app.layoutView.render();
	console.log("---- App started ----");
});