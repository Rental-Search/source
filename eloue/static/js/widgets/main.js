require.config({
    baseUrl: "/static/js/widgets",
    paths: {
        "bootstrap": "/static/bower_components/bootstrap/dist/js/bootstrap.min",
        "lodash": "/static/bower_components/lodash/dist/lodash.min",
        "jQuery": "/static/bower_components/jquery/dist/jquery.min",
        "jquery-ui": "/static/bower_components/jqueryui/jquery-ui.min",
        "slider": "/static/bower_components/jqueryui/ui/minified/slider.min",
        "core": "/static/bower_components/jqueryui/ui/minified/core.min",
        "mouse": "/static/bower_components/jqueryui/ui/minified/mouse.min",
        "widget": "/static/bower_components/jqueryui/ui/minified/widget.min",
        "angular": "/static/bower_components/angular/angular.min",
        "angular-resource": "/static/bower_components/angular-resource/angular-resource.min",
        "angular-route": "/static/bower_components/angular-route/angular-route.min",
        "angular-cookies": "/static/bower_components/angular-cookies/angular-cookies.min",
        "angular-sanitize": "/static/bower_components/angular-sanitize/angular-sanitize.min",
        "moment": "/static/bower_components/moment/min/moment.min",
        "angular-moment": "/static/bower_components/angular-moment/angular-moment.min",
        "bootstrap-datepicker": "/static/bower_components/bootstrap-datepicker/js/bootstrap-datepicker",
        "bootstrap-datepicker-fr": "/static/bower_components/bootstrap-datepicker/js/locales/bootstrap-datepicker.fr",
        "datejs": "/static/bower_components/datejs/build/production/date.min",
        "chosen": "/static/bower_components/chosen/chosen.jquery.min",
        "html5shiv": "/static/bower_components/html5shiv/dist/html5shiv.min",
        "respond": "/static/bower_components/respond/respond.min",
        "placeholders-utils": "/static/bower_components/placeholders/lib/utils",
        "placeholders-main": "/static/bower_components/placeholders/lib/main",
        "placeholders-jquery": "/static/bower_components/placeholders/lib/adapters/placeholders.jquery",
        "custom-scrollbar": "/static/bower_components/malihu-custom-scrollbar-plugin/jquery.mCustomScrollbar",
        "jquery-mousewheel": "/static/bower_components/jquery-mousewheel/jquery.mousewheel",
        "toastr": "/static/bower_components/toastr/toastr.min",
        "formmapper": "/static/js/formmapper"
    },
    shim: {
        "angular": {"exports": "angular"},
        "angular-route": ["angular"],
        "angular-cookies": ["angular"],
        "angular-sanitize": ["angular"],
        "angular-resource": ["angular"],
        "angular-moment": ["angular"],
        "angular-mocks": {
            deps: ["angular"],
            "exports": "angular.mock"
        },
        "jQuery": {exports: "jQuery"},
        "jquery-ui": ["jQuery"],
        "slider": ["jQuery"],
        "core": ["jQuery"],
        "mouse": ["jQuery"],
        "widget": ["jQuery"],
        "bootstrap": ["jQuery"],
        "moment": ["jQuery"],
        "bootstrap-datepicker": ["jQuery"],
        "bootstrap-datepicker-fr": ["jQuery", "bootstrap-datepicker"],
        "chosen": ["jQuery"],
        "placeholders-jquery": ["jQuery"],
        "formmapper": ["jQuery"],
        "jquery-mousewheel": ["jQuery"],
        "custom-scrollbar": ["jQuery", "jquery-mousewheel"],
        "toastr": ["jQuery"]
    }
});

require([
    "jQuery",
    "lodash",
    "angular",
    "bootstrap",
    "moment",
    "angular-moment",
    "datejs",
    "chosen",
    "html5shiv",
    "respond",
    "placeholders-utils",
    "placeholders-main",
    "placeholders-jquery",
    "formmapper",
    "toastr",
//    "jquery-ui",
    "slider",
    "core",
    "mouse",
    "widget",
    "bootstrap-datepicker",
    "bootstrap-datepicker-fr",
    "eloue/route"
], function ($, _, angular) {
    "use strict";
    $(function () {
        $("select").attr("eloue-chosen", "");

        angular.bootstrap(document, ["EloueApp"]);

        var slide_imgs = [].slice.call($('.carousel-wrapper').find('img'));
        for (var index = 0; index < slide_imgs.length; index++) {
            var proportions = $(slide_imgs[index]).width() / $(slide_imgs[index]).height(),
                parent = $(slide_imgs[index]).parent(),
                parent_proportions = $(parent).width() / $(parent).height();

            if (proportions < parent_proportions) {
                $(slide_imgs[index]).addClass('expand-v');
            } else {
                $(slide_imgs[index]).addClass('expand-h');
            }
        }

        var layout_switcher = $('.layout-switcher'), article = $('article');
        if (layout_switcher && article) {
            // switch grid/list layouts
            $(layout_switcher).on('click', 'i', function () {
                if ($(this).hasClass('grid')) {
                    article.removeClass('list-layout');
                    article.addClass('grid-layout')
                } else {
                    article.removeClass('grid-layout');
                    article.addClass('list-layout')

                }
            });
        }

        var districtFake = $("#district-fake"), priceFake = $("#price-fake");
        if (districtFake) {
            districtFake.slider({
                range: "min",
                value: 400,
                min: 1,
                max: 700
            });
        }

        if (priceFake) {
            priceFake.slider({
                range: true,
                min: 0,
                max: 700,
                values: [100, 400]
            });
        }

        (function (d, s, id) {
            var js, fjs = d.getElementsByTagName(s)[0];
            if (d.getElementById(id)) return;
            js = d.createElement(s);
            js.id = id;
            js.src = "//connect.facebook.net/en_US/sdk.js#xfbml=1&version=v2.0";
            fjs.parentNode.insertBefore(js, fjs);
        }(document, 'script', 'facebook-jssdk'));

        window.___gcfg = {lang: 'fr'};
        (function () {
            var po = document.createElement('script');
            po.type = 'text/javascript';
            po.async = true;
            po.src = 'https://apis.google.com/js/platform.js';
            var s = document.getElementsByTagName('script')[0];
            s.parentNode.insertBefore(po, s);
        })();

        !function (d, s, id) {
            var js, fjs = d.getElementsByTagName(s)[0], p = /^http:/.test(d.location) ? 'http' : 'https';
            if (!d.getElementById(id)) {
                js = d.createElement(s);
                js.id = id;
                js.src = p + '://platform.twitter.com/widgets.js';
                fjs.parentNode.insertBefore(js, fjs);
            }
        }(document, 'script', 'twitter-wjs');

        // Insert YouTube video into defined container, add play on modal open and stop on modal hide
        var tag = document.createElement('script');

        tag.src = "https://www.youtube.com/iframe_api";
        var firstScriptTag = document.getElementsByTagName('script')[0];
        firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
        var videoModal = $('#videoModal');
        var player;

        videoModal.on('shown.bs.modal', function () {
            player = new YT.Player('videoContainer', {
                height: '480',
                width: '640',
                videoId: 'nERu_2pSSb0',
                events: {
                    'onReady': onPlayerReady
                }
            });
        });
        videoModal.on('hidden.bs.modal', function () {
            player.destroy();
        });

        function onPlayerReady(event) {
            event.target.playVideo();
        }

        $('#geolocate').formmapper({
            details: "form"
        });

    });
});