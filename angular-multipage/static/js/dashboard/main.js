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
        "angular-translate": "../../bower_components/angular-translate/angular-translate.min",
        "jquery-form": "../../bower_components/jquery-form/jquery.form",
        "selectivizr": "../../bower_components/selectivizr/selectivizr",
        "jquery-mousewheel": "../../bower_components/jquery-mousewheel/jquery.mousewheel",
        "custom-scrollbar": "../../bower_components/malihu-custom-scrollbar-plugin/jquery.mCustomScrollbar",
        "jquery-autosize": "../../bower_components/jquery-autosize/jquery.autosize.min",
        "jquery-chosen": "../../js/chosen.jquery.min",
        "vars": "../vars",
        "bootstrap_modal": "../bootstrap/modal"
    },
    shim: {
        "angular": {"exports": "angular"},
        "angular-route": ["angular"],
        "angular-cookies": ["angular"],
        "angular-sanitize": ["angular"],
        "angular-resource": ["angular"],
        "angular-ui-router": ["angular"],
        "angular-translate": ["angular"],
        "angular-mocks": {
            deps: ["angular"],
            "exports": "angular.mock"
        },
        "jQuery": {exports: "jQuery"},
        "bootstrap": ["jQuery"],
        "jquery-form": ["jQuery"],
        "selectivizr": ["jQuery"],
        "jquery-mousewheel": ["jQuery"],
        "custom-scrollbar": ["jQuery", "jquery-mousewheel"],
        "jquery-autosize": ["jQuery"],
        "jquery-chosen": ["jQuery"],
        "bootstrap_modal":  ["jQuery"]
    }
});

require([
    "jQuery",
    "lodash",
    "angular",
    "bootstrap",
    "vars",
    "eloue/route",
    "eloue/i18n"
], function ($, _, angular, bootstrap, vars, route) {
    "use strict";
    $(function () {
        angular.bootstrap(document, ["EloueDashboardApp"]);
    });
});