require.config({
    baseUrl: "../static/js/dashboard",
    paths: {
        "bootstrap": "../../bower_components/bootstrap/dist/js/bootstrap.min",
        "lodash": "../../bower_components/lodash/dist/lodash.min",
        "jQuery": "../../bower_components/jquery/dist/jquery.min",
        "angular": "../../bower_components/angular/angular.min",
        "angular-resource": "../../bower_components/angular-resource/angular-resource.min",
        "angular-route": "../../bower_components/angular-route/angular-route.min",
        "angular-cookies": "../../bower_components/angular-cookies/angular-cookies.min",
        "angular-sanitize": "../../bower_components/angular-sanitize/angular-sanitize.min",
        "angular-ui-router": "../../bower_components/angular-ui-router/release/angular-ui-router.min",
        "angular-file-reader": "../../bower_components/angular-filereader/src/filereader.service",
        "vars": "../vars"
    },
    shim: {
        "angular": {"exports": "angular"},
        "angular-route": ["angular"],
        "angular-cookies": ["angular"],
        "angular-sanitize": ["angular"],
        "angular-resource": ["angular"],
        "angular-ui-router": ["angular"],
        "angular-mocks": {
            deps: ["angular"],
            "exports": "angular.mock"
        },
        "jQuery": {exports: "jQuery"},
        "bootstrap": ["jQuery"]
    }
});

require([
    "jQuery",
    "lodash",
    "angular",
    "bootstrap",
    "vars",
    "eloue/route"
], function ($, _, angular, bootstrap, vars, route) {
    "use strict";
    $(function () {
        angular.bootstrap(document, ["EloueDashboardApp"]);
    });
});