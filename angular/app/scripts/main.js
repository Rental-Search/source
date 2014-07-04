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
        "angular-sanitize": "../bower_components/angular-sanitize/angular-sanitize.min"
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
        "bootstrap": ["jQuery"]
    },
    priority: [
        "angular"
    ]
});

//http://code.angularjs.org/1.2.1/docs/guide/bootstrap#overview_deferred-bootstrap
window.name = "NG_DEFER_BOOTSTRAP!";

require([
    "jQuery",
    "bootstrap",
    "angular",
    "app",
    "angular-route",
    "angular-cookies",
    "angular-sanitize",
    "angular-resource"
], function ($, bootstrap, angular, app, ngRoutes, ngCookies, ngSanitize, ngResource) {
    "use strict";
    /* jshint ignore:start */
    var $html = angular.element(document.getElementsByTagName("html")[0]);
    /* jshint ignore:end */
    angular.element().ready(function () {
        angular.resumeBootstrap([app.name]);
    });
});