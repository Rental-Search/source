$(document).ready(function(){
	var classic_form = $('.classic-form');
	classic_form.hide();
	$('#geolocate').formmapper({
		details: 'form',
	});
	$('.registration').on('click', function(){
		classic_form.slideDown();
		$(this).slideUp();
		console.log($(this))
	});
	$('select').chosen();

	var slide_imgs = [].slice.call($('.carousel-wrapper').find('img'));
	for(var index = 0; index < slide_imgs.length; index++) {
		var proportions = $(slide_imgs[index]).width() / $(slide_imgs[index]).height(),
				parent = $(slide_imgs[index]).parent(),
				parent_proportions = $(parent).width() / $(parent).height();

		if(proportions < parent_proportions) {
			$(slide_imgs[index]).addClass('expand-v');
		} else {
			$(slide_imgs[index]).addClass('expand-h');
		}
		console.log(slide_imgs.length);
	};
});
