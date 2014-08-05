$(document).ready(function() {
  var dashboard = {
        article: $('.dashboard'),
        nav: $('.dashboard').find('nav').find('ul'),
      };

  function setProperties() {
    var article_height = $(window).height() - $('header').height(),
        nav_fz = {
          current: parseFloat(dashboard.nav.css('font-size')),
          max: 12
        };

    // set article height
    dashboard.article.height(article_height);

    // set nav font-size
    while(dashboard.nav.height() < article_height && nav_fz.max > nav_fz.current) {
      dashboard.nav.css('font-size', ++nav_fz.current + 'px');
    }
    while(dashboard.nav.height() >= article_height) {
      dashboard.nav.css('font-size', --nav_fz.current + 'px');
    }

  }

  setProperties();

  $(window).on('resize', function() {
    setProperties();
  });

  // custom select
  $('select').chosen();

  // custom scrollbar
  $('.chosen-drop').mCustomScrollbar({
    scrollInertia: '200',
    autoHideScrollbar: true,
    theme: 'dark-thin',
    scrollbarPosition: 'outside',
    advanced:{
      autoScrollOnFocus: false
    }
  });
  $('.scrollbar-custom').mCustomScrollbar({
    scrollInertia: '200',
    autoHideScrollbar: true,
    theme: 'dark-thin',
    advanced:{
      autoScrollOnFocus: false
    }
  });


  // autoewsize textarea's
  $('textarea').autosize();
});