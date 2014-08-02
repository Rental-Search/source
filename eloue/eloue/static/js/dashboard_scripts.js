$(document).ready(function() {
  var dashboard = {
        article: $('.dashboard'),
        nav: $('.dashboard').find('nav').find('ul'),
      };


  function setPhysicalProperties() {
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

  setPhysicalProperties();

  $(window).on('resize', function() {
    setPhysicalProperties();
  });

  $('.scrollbar-custom').mCustomScrollbar({
    scrollInertia: '200',
    autoHideScrollbar: true,
    theme: 'dark-thin',
    SetWidth: true
  });
});