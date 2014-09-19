require.config({
    baseUrl: "/static/js/widgets",
    paths: {
        "bootstrap": "/static/bower_components/bootstrap/dist/js/bootstrap.min",
        "lodash": "/static/bower_components/lodash/dist/lodash.min",
        "jQuery": "/static/bower_components/jquery/dist/jquery.min",
        "angular": "/static/bower_components/angular/angular.min",
        "angular-resource": "/static/bower_components/angular-resource/angular-resource.min",
        "angular-route": "/static/bower_components/angular-route/angular-route.min",
        "angular-cookies": "/static/bower_components/angular-cookies/angular-cookies.min",
        "angular-sanitize": "/static/bower_components/angular-sanitize/angular-sanitize.min",
        "moment": "/static/bower_components/moment/min/moment.min",
        "angular-moment": "/static/bower_components/angular-moment/angular-moment.min",
        "bootstrap-datepicker": "/static/bower_components/bootstrap-datepicker/js/bootstrap-datepicker",
        "datejs": "/static/bower_components/datejs/build/production/date.min",
        "chosen": "/static/bower_components/chosen/chosen.jquery.min",
        "html5shiv": "/static/bower_components/html5shiv/dist/html5shiv.min",
        "respond": "/static/bower_components/respond/respond.min",
        "placeholders-utils": "/static/bower_components/placeholders/lib/utils",
        "placeholders-main": "/static/bower_components/placeholders/lib/main",
        "placeholders-jquery": "/static/bower_components/placeholders/lib/adapters/placeholders.jquery",
        "angular-chosen-localytics": "/static/bower_components/angular-chosen-localytics/chosen",
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
        "angular-chosen-localytics": ["angular"],
        "angular-mocks": {
            deps: ["angular"],
            "exports": "angular.mock"
        },
        "jQuery": {exports: "jQuery"},
        "bootstrap": ["jQuery"],
        "moment": ["jQuery"],
        "bootstrap-datepicker": ["jQuery"],
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
    "bootstrap-datepicker",
    "datejs",
    "chosen",
    "html5shiv",
    "respond",
    "placeholders-utils",
    "placeholders-main",
    "placeholders-jquery",
    "angular-chosen-localytics",
    "formmapper",
    "toastr",
    "eloue/route"
], function ($, _, angular) {
    "use strict";
    $(function () {
        angular.bootstrap(document, ["EloueApp"]);
        $('#geolocate').formmapper({
            details: "form"
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
        }
    });
});