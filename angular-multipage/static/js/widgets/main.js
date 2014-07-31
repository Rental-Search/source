require.config({
    baseUrl: "../static/js/widgets",
    paths: {
        "bootstrap": "../../bower_components/bootstrap/dist/js/bootstrap.min",
        "lodash": "../../bower_components/lodash/dist/lodash.min",
        "jQuery": "../../bower_components/jquery/dist/jquery.min",
        "angular": "../../bower_components/angular/angular.min",
        "angular-resource": "../../bower_components/angular-resource/angular-resource.min",
        "angular-route": "../../bower_components/angular-route/angular-route.min",
        "angular-cookies": "../../bower_components/angular-cookies/angular-cookies.min",
        "angular-sanitize": "../../bower_components/angular-sanitize/angular-sanitize.min",
        "moment": "../../bower_components/moment/min/moment.min",
        "angular-moment": "../../bower_components/angular-moment/angular-moment.min",
        "bootstrap-datepicker": "../../bower_components/bootstrap-datepicker/js/bootstrap-datepicker",
        "datejs": "../../bower_components/datejs/build/production/date.min",
        "chosen": "../../bower_components/chosen/chosen.jquery.min",
        "html5shiv": "../../bower_components/html5shiv/dist/html5shiv.min",
        "respond": "../../bower_components/respond/respond.min",
        "placeholders-utils": "../../bower_components/placeholders/lib/utils",
        "placeholders-main": "../../bower_components/placeholders/lib/main",
        "placeholders-jquery": "../../bower_components/placeholders/lib/adapters/placeholders.jquery",
        "formmapper": "../formmapper",
        "vars": "../vars"
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
        "bootstrap": ["jQuery"],
        "moment": ["jQuery"],
        "bootstrap-datepicker": ["jQuery"],
        "chosen": ["jQuery"],
        "placeholders-jquery": ["jQuery"],
        "formmapper": ["jQuery"]
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
    "formmapper",
    "vars",
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