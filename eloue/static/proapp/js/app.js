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
	console.log("---- App started ----");
});