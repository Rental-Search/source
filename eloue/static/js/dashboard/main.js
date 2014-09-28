require.config({
    baseUrl: "/static/js/dashboard",
    paths: {
        "bootstrap": "/static/bower_components/bootstrap/dist/js/bootstrap.min",
        "underscore": "/static/bower_components/lodash/dist/lodash.min",
        "jQuery": "/static/bower_components/jquery/dist/jquery.min",
        "angular": "/static/bower_components/angular/angular.min",
        "angular-resource": "/static/bower_components/angular-resource/angular-resource.min",
        "angular-route": "/static/bower_components/angular-route/angular-route.min",
        "angular-cookies": "/static/bower_components/angular-cookies/angular-cookies.min",
        "angular-sanitize": "/static/bower_components/angular-sanitize/angular-sanitize.min",
        "angular-ui-router": "/static/bower_components/angular-ui-router/release/angular-ui-router.min",
        "angular-translate": "/static/bower_components/angular-translate/angular-translate.min",
        "bootstrap-datepicker": "/static/bower_components/bootstrap-datepicker/js/bootstrap-datepicker",
        "jquery-form": "/static/bower_components/jquery-form/jquery.form",
        "datejs": "/static/bower_components/datejs/build/production/date.min",
        "selectivizr": "/static/bower_components/selectivizr/selectivizr",
        "jquery-mousewheel": "/static/bower_components/jquery-mousewheel/jquery.mousewheel",
        "custom-scrollbar": "/static/bower_components/malihu-custom-scrollbar-plugin/jquery.mCustomScrollbar",
        "jquery-autosize": "/static/bower_components/jquery-autosize/jquery.autosize.min",
        "jquery-chosen": "/static/bower_components/chosen/chosen.jquery.min",
        "toastr": "/static/bower_components/toastr/toastr.min",
        "formmapper": "/static/js/formmapper"
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
        "bootstrap-datepicker": ["jQuery"],
        "toastr": ["jQuery"],
        "formmapper": ["jQuery"]
    }
});

require([
    "jQuery",
    "underscore",
    "angular",
    "bootstrap",
    "datejs",
    "bootstrap-datepicker",
    "formmapper",
    "toastr",
    "eloue/route",
    "eloue/i18n"
], function ($, _, angular, bootstrap, route) {
    "use strict";
    $(function () {
        angular.bootstrap(document, ["EloueDashboardApp"]);
    });
});