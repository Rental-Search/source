$(document).ready(function(){
  var classic_form = $('.classic-form'),
      article = $('article');
      
  classic_form.hide();
  $('#geolocate').formmapper({
    details: 'form',
  });
  $('.registration').on('click', function(){
    classic_form.slideDown();
    $(this).slideUp();
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
  };

  $('.date-picker input.date').datepicker({
    language: "fr",
    autoclose: true,
    todayHighlight: true
  });

  (function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) return;
    js = d.createElement(s); js.id = id;
    js.src = "//connect.facebook.net/en_US/sdk.js#xfbml=1&version=v2.0";
    fjs.parentNode.insertBefore(js, fjs);
  }(document, 'script', 'facebook-jssdk'));

  window.___gcfg = {lang: 'fr'};
    (function() {
      var po = document.createElement('script'); po.type = 'text/javascript'; po.async = true;
      po.src = 'https://apis.google.com/js/platform.js';
      var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(po, s);
    })();



  !function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+'://platform.twitter.com/widgets.js';fjs.parentNode.insertBefore(js,fjs);}}(document, 'script', 'twitter-wjs');
});
