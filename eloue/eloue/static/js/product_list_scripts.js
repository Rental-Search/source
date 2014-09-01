$(document).ready(function(){
  var layout_switcher = $('.layout-switcher'),
      article = $('article');
  // switch grid/list layouts
  $(layout_switcher).on('click', 'i', function(){
    if($(this).hasClass('sprite-grid')) {
      article.removeClass('list-layout')
      article.addClass('grid-layout')
    } else {
      article.removeClass('grid-layout')
      article.addClass('list-layout')
      
    }
  });

   $( "#district-fake" ).slider({
    range: "min",
    value: 400,
    min: 1,
    max: 700,
  });

   $( "#price-fake" ).slider({
    range: true,
    min: 0,
    max: 700,
    values: [100,400],
  });
});
