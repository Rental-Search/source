require.config({
    baseUrl: "../static/js/homepage",
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
    "formmapper",
    "vars",
    "eloue/route"
], function ($, _, angular, bootstrap, moment, ngMoment, datepicker, datejs, formmapper, vars, route) {
    "use strict";
    $(function () {
        angular.bootstrap($("#ngModals"), ["EloueApp"]);
        $('#geolocate').formmapper({
            details: "form"
        });
    });
});
