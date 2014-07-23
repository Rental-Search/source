$(document).ready(function(){
	var classic_form = $('.classic-form');
	classic_form.hide();
	$('#geolocate').formmapper({
		details: "form",
	});
	$('.registration').on('click', function(){
		classic_form.slideDown();
		$(this).slideUp();
		console.log($(this))
	});
	$("select").chosen();
});
