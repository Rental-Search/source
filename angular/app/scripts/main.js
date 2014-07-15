/*jshint unused: vars */
require.config({
    baseUrl: "../scripts",
    paths: {
        "bootstrap": "../bower_components/bootstrap/dist/js/bootstrap.min",
        "jQuery": "../bower_components/jquery/dist/jquery.min",
        "angular": "../bower_components/angular/angular.min",
        "angular-resource": "../bower_components/angular-resource/angular-resource.min",
        "angular-route": "../bower_components/angular-route/angular-route.min",
        "angular-cookies": "../bower_components/angular-cookies/angular-cookies.min",
        "angular-sanitize": "../bower_components/angular-sanitize/angular-sanitize.min",
        "bootstrap-datepicker": "../bower_components/bootstrap-datepicker/js/bootstrap-datepicker",
        "bootstrap-timepicker": "../bower_components/bootstrap-timepicker/js/bootstrap-timepicker"
    },
    shim: {
        "angular": {"exports": "angular"},
        "angular-route": ["angular"],
        "angular-cookies": ["angular"],
        "angular-sanitize": ["angular"],
        "angular-resource": ["angular"],
        "angular-mocks": {
            deps: ["angular"],
            "exports": "angular.mock"
        },
        "jQuery": {exports: "jQuery"},
        "bootstrap": ["jQuery"],
        "bootstrap-datepicker": ["jQuery"],
        "bootstrap-timepicker": ["jQuery"]
    }
});

require([
    "jQuery",
    "angular",
    "bootstrap",
    "bootstrap-datepicker",
    "bootstrap-timepicker",
    "eloue/route"
], function ($, angular, bootstrap, datepicker, timepicker, route) {
    "use strict";
    $(function () {
        angular.bootstrap(document, ["EloueApp"]);
    });
});