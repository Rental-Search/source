var STATIC_URL = "/static/";
var scripts = document.getElementsByTagName('script');
for(var i = 0, l = scripts.length; i < l; i++){
    if(scripts[i].src.indexOf('require.js') != -1){
        STATIC_URL = scripts[i].getAttribute('data-static-path');
        break;
    }
}
require.config({
    baseUrl: STATIC_URL + "js/dashboard",
    paths: {
        "bootstrap": STATIC_URL + "bower_components/bootstrap/dist/js/bootstrap.min",
        "underscore": STATIC_URL + "bower_components/lodash/dist/lodash.min",
        "jQuery": STATIC_URL + "bower_components/jquery/dist/jquery.min",
        "angular": STATIC_URL + "bower_components/angular/angular.min",
        "angular-resource": STATIC_URL + "bower_components/angular-resource/angular-resource.min",
        "angular-route": STATIC_URL + "bower_components/angular-route/angular-route.min",
        "angular-cookies": STATIC_URL + "bower_components/angular-cookies/angular-cookies.min",
        "angular-sanitize": STATIC_URL + "bower_components/angular-sanitize/angular-sanitize.min",
        "angular-ui-router": STATIC_URL + "bower_components/angular-ui-router/release/angular-ui-router.min",
        "angular-translate": STATIC_URL + "bower_components/angular-translate/angular-translate.min",
        "bootstrap-datepicker": STATIC_URL + "bower_components/bootstrap-datepicker/js/bootstrap-datepicker",
        "bootstrap-datepicker-fr": STATIC_URL + "bower_components/bootstrap-datepicker/js/locales/bootstrap-datepicker.fr",
        "jquery-form": STATIC_URL + "bower_components/jquery-form/jquery.form",
        "datejs": STATIC_URL + "bower_components/datejs/build/production/date.min",
        "chosen": STATIC_URL + "bower_components/chosen/chosen.jquery.min",
        "selectivizr": STATIC_URL + "bower_components/selectivizr/selectivizr",
        "jquery-mousewheel": STATIC_URL + "bower_components/jquery-mousewheel/jquery.mousewheel",
        "custom-scrollbar": STATIC_URL + "bower_components/malihu-custom-scrollbar-plugin/jquery.mCustomScrollbar",
        "jquery-autosize": STATIC_URL + "bower_components/jquery-autosize/jquery.autosize.min",
        "toastr": STATIC_URL + "bower_components/toastr/toastr.min",
        "formmapper": STATIC_URL + "js/formmapper"
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
        "bootstrap-datepicker": ["jQuery"],
        "bootstrap-datepicker-fr": ["jQuery", "bootstrap-datepicker"],
        "chosen": ["jQuery"],
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
    "chosen",
    "bootstrap-datepicker",
    "bootstrap-datepicker-fr",
    "formmapper",
    "toastr",
    "../common/eloue/commonApp",
    "eloue/route",
    "eloue/i18n"
], function ($, _, angular, bootstrap, route) {
    "use strict";
    $(function () {

        angular.bootstrap(document, ["EloueDashboardApp"]);
    });
});