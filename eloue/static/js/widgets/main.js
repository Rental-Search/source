require.config(
    (function () {
        var STATIC_URL = "/static/";
        var scripts = document.getElementsByTagName("script");
        for (var i = 0, l = scripts.length; i < l; i++) {
            if (scripts[i].getAttribute("data-static-path")) {
                STATIC_URL = scripts[i].getAttribute("data-static-path");
                break;
            }
        }
        return {
            baseUrl: STATIC_URL + "js/widgets",
            paths: {
                "bootstrap": "../../bower_components/bootstrap/dist/js/bootstrap",
                "lodash": "../../bower_components/lodash/lodash",
                "jquery": "../../bower_components/jquery/dist/jquery",
                "jquery-ui": "../../bower_components/jqueryui/jquery-ui",
                "jshashtable": "../jshashtable-2.1_src",
                "jquery.numberformatter": "../jquery.numberformatter-1.2.3",
                "tmpl": "../tmpl",
                "jquery.dependClass": "../jquery.dependClass-0.1",
                "draggable": "../draggable-0.1",
                "slider": "../jquery.slider",
                "smartbanner": "../jquery.smartbanner",
                "core": "../../bower_components/jqueryui/ui/core",
                "mouse": "../../bower_components/jqueryui/ui/mouse",
                "widget": "../../bower_components/jqueryui/ui/widget",
                "angular": "../../bower_components/angular/angular",
                "angular-resource": "../../bower_components/angular-resource/angular-resource",
                "angular-cookies": "../../bower_components/angular-cookies/angular-cookies",
                "angular-sanitize": "../../bower_components/angular-sanitize/angular-sanitize",
                "angular-i18n": "../../bower_components/angular-i18n/angular-locale_fr-fr",
                "angular-translate": "../../bower_components/angular-translate/angular-translate",
                "moment": "../../bower_components/moment/moment",
                "angular-moment": "../../bower_components/angular-moment/angular-moment",
                "bootstrap-datepicker": "../../bower_components/bootstrap-datepicker/js/bootstrap-datepicker",
                "bootstrap-datepicker-fr": "../../bower_components/bootstrap-datepicker/js/locales/bootstrap-datepicker.fr",
                "jquery-form": "../../bower_components/jquery-form/jquery.form",
                "datejs": "../../bower_components/datejs/build/date",
                "chosen": "../../bower_components/chosen/chosen.jquery",
                "html5shiv": "../../bower_components/html5shiv/dist/html5shiv",
                "respond": "../../bower_components/respond/respond.src",
                "placeholders-utils": "../../bower_components/placeholders/lib/utils",
                "placeholders-main": "../../bower_components/placeholders/lib/main",
                "placeholders-jquery": "../../bower_components/placeholders/lib/adapters/placeholders.jquery",
                "custom-scrollbar": "../../bower_components/malihu-custom-scrollbar-plugin/jquery.mCustomScrollbar",
                "jquery-mousewheel": "../../bower_components/jquery-mousewheel/jquery.mousewheel",
                "toastr": "../../bower_components/toastr/toastr",
                "formmapper": "../formmapper",
                "filesaver": "../FileSaver.min",
                "angular-cookie": "../../bower_components/angular-cookie/angular-cookie",
                "algoliasearch": "../../bower_components/algoliasearch/dist/algoliasearch.angular",
                "algoliasearch-helper": "../../bower_components/algoliasearch-helper/dist/algoliasearch.helper",
                "angularjs-slider": "../../bower_components/angularjs-slider/dist/rzslider",
                "nemSimpleLogger": "../../bower_components/angular-simple-logger/dist/angular-simple-logger",
                "uiGmapgoogle-maps": "../../bower_components/angular-google-maps/dist/angular-google-maps",
                "js-cookie": "../../bower_components/js-cookie/src/js.cookie",
                "stacktrace": "../../bower_components/stacktrace-js/stacktrace",
                "stack-generator": "../../bower_components/stack-generator/stack-generator",
                "stackframe": "../../bower_components/stackframe/stackframe",
                "error-stack-parser": "../../bower_components/error-stack-parser/error-stack-parser",
                "stacktrace-gps": "../../bower_components/stacktrace-gps/stacktrace-gps",
                "source-map": "../../bower_components/source-map/source-map"
            },
            shim: {
                "angular": {
                    deps: ["jquery"],
                    "exports": "angular"
                },
                "angular-cookies": ["angular"],
                "angular-sanitize": ["angular"],
                "angular-i18n": ["angular"],
                "angular-translate": ["angular"],
                "angular-resource": ["angular"],
                "angular-moment": ["angular"],
                "angular-mocks": {
                    deps: ["angular"],
                    "exports": "angular.mock"
                },
                "jquery": {exports: "jquery"},
                "jquery-ui": ["jquery"],
                "jshashtable": ["jquery"],
                "jquery.numberformatter": ["jquery"],
                "tmpl": ["jquery"],
                "jquery.dependClass": ["jquery"],
                "draggable": ["jquery"],
                "slider": ["jquery"],
                "smartbanner": ["jquery"],
                "core": ["jquery"],
                "mouse": ["jquery"],
                "widget": ["jquery"],
                "bootstrap": ["jquery"],
                "jquery-form": ["jquery"],
                "moment": ["jquery"],
                "bootstrap-datepicker": ["jquery"],
                "bootstrap-datepicker-fr": ["jquery", "bootstrap-datepicker"],
                "chosen": ["jquery"],
                "placeholders-jquery": ["jquery"],
                "formmapper": ["jquery"],
                "jquery-mousewheel": ["jquery"],
                "custom-scrollbar": ["jquery", "jquery-mousewheel"],
                "toastr": ["jquery"],
                "angular-cookie": ["angular"],
                "algoliasearch": ["angular"],
                "algoliasearch-helper": ["algoliasearch"],
                "angularjs-slider": ["angular"],
                "nemSimpleLogger": ["angular"],
                "uiGmapgoogle-maps": ["angular", "lodash", "nemSimpleLogger"],
                "stacktrace": ["error-stack-parser", "stack-generator", "stacktrace-gps"],
                "error-stack-parser": ["stackframe"],
                "stacktrace-gps": ["source-map"],
                "js-cookie": {exports: "Cookies"}
            }
        };
    })()
);

require([
    "jquery",
    "lodash",
    "angular",
    "bootstrap",
    "moment",
    "angular-moment",
    "datejs",
    "chosen",
    "html5shiv",
    "respond",
    "placeholders-utils",
    "placeholders-main",
    "placeholders-jquery",
    "formmapper",
    "filesaver",
    "jquery-mousewheel",
    "custom-scrollbar",
    "toastr",
    "jquery-form",
//    "jquery-ui",
    "jshashtable",
    "jquery.numberformatter",
    "tmpl",
    "jquery.dependClass",
    "draggable",
    "slider",
    "smartbanner",
    "core",
    "mouse",
    "widget",
    "bootstrap-datepicker",
    "bootstrap-datepicker-fr",
    "../common/eloue/commonApp",
    "../common/eloue/i18n",
    "eloue/config",
    "angular-cookie",
    "algoliasearch",
    "algoliasearch-helper",
    "angularjs-slider",
    "nemSimpleLogger",
    "uiGmapgoogle-maps",
    "js-cookie",
    "stacktrace"
], function ($, _, angular) {
    "use strict";
    $(function () {
        $(".signs-links").find("ul.without-spaces").show();
        angular.bootstrap(document, ["EloueWidgetsApp"]);
    });
});
