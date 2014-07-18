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
        "moment": "../bower_components/moment/min/moment.min",
        "angular-moment":"../bower_components/angular-moment/angular-moment.min",
        "eonasdan-bootstrap-datetimepicker": "../bower_components/eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min",
"datejs": "../bower_components/datejs/build/production/date.min"
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
        "eonasdan-bootstrap-datetimepicker": ["jQuery"]
    }
});

require([
    "jQuery",
    "angular",
    "bootstrap",
    "moment",
    "angular-moment",
    "eonasdan-bootstrap-datetimepicker",
    "datejs",
    "eloue/route"
], function ($, angular, bootstrap, moment, ngMoment, datetimepicker, datejs, route) {
    "use strict";
    $(function () {
        angular.bootstrap(document, ["EloueApp"]);
    });
});