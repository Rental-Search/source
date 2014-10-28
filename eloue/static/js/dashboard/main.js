require.config(
    (function () {
        var STATIC_URL = "/static/";
        var scripts = document.getElementsByTagName('script');
        for (var i = 0, l = scripts.length; i < l; i++) {
            if (scripts[i].getAttribute('data-static-path')) {
                STATIC_URL = scripts[i].getAttribute('data-static-path');
                break;
            }
        }
        return {
            baseUrl: STATIC_URL + "js/dashboard",
            paths: {
                "bootstrap": "../../bower_components/bootstrap/dist/js/bootstrap.min",
                "underscore": "../../bower_components/lodash/dist/lodash.min",
                "jQuery": "../../bower_components/jquery/dist/jquery.min",
                "angular": "../../bower_components/angular/angular.min",
                "angular-resource": "../../bower_components/angular-resource/angular-resource.min",
                "angular-route": "../../bower_components/angular-route/angular-route.min",
                "angular-cookies": "../../bower_components/angular-cookies/angular-cookies.min",
                "angular-sanitize": "../../bower_components/angular-sanitize/angular-sanitize.min",
                "angular-ui-router": "../../bower_components/angular-ui-router/release/angular-ui-router.min",
                "angular-translate": "../../bower_components/angular-translate/angular-translate.min",
                "bootstrap-datepicker": "../../bower_components/bootstrap-datepicker/js/bootstrap-datepicker",
                "bootstrap-datepicker-fr": "../../bower_components/bootstrap-datepicker/js/locales/bootstrap-datepicker.fr",
                "jquery-form": "../../bower_components/jquery-form/jquery.form",
                "datejs": "../../bower_components/datejs/build/production/date.min",
                "chosen": "../../bower_components/chosen/chosen.jquery.min",
                "selectivizr": "../../bower_components/selectivizr/selectivizr",
                "jquery-mousewheel": "../../bower_components/jquery-mousewheel/jquery.mousewheel",
                "custom-scrollbar": "../../bower_components/malihu-custom-scrollbar-plugin/jquery.mCustomScrollbar",
                "jquery-autosize": "../../bower_components/jquery-autosize/jquery.autosize.min",
                "toastr": "../../bower_components/toastr/toastr.min",
                "formmapper": "../formmapper"
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
        }
    })()
);

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

        var load_google_analytics = function () {
            var script = document.createElement("script");
            script.type = "text/javascript";
            var code = "(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){" +
                "(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o)," +
                "m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)" +
                "})(window,document,'script','//www.google-analytics.com/analytics.js','ga');" +
                "ga('create', 'UA-8258979-7', 'e-loue.com');" +
                "ga('send', 'pageview');";
            try {
                script.appendChild(document.createTextNode(code));
                document.body.appendChild(script);
            } catch (e) {
                script.text = code;
                document.body.appendChild(script);
            }
        };

        load_google_analytics();
    });
});