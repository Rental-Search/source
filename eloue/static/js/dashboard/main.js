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
                "formmapper": "../formmapper",
                "filesaver": "../FileSaver.min"
            },
            shim: {
                "angular": {
                    deps: ["jQuery"],
                    "exports": "angular"
                },
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
    "filesaver",
    "jquery-mousewheel",
    "custom-scrollbar",
    "toastr",
    "../common/eloue/commonApp",
    "../common/eloue/i18n",
    "eloue/route"
], function ($, _, angular, bootstrap, route) {
    "use strict";
    $(function () {
        $(".signs-links").find("ul.without-spaces").show();
        angular.bootstrap(document, ["EloueDashboardApp"]);
    });
    (function (d, s, id) {
        var js, fjs = d.getElementsByTagName(s)[0];
        if (d.getElementById(id)) return;
        js = d.createElement(s);
        js.id = id;
        js.src = "//connect.facebook.net/fr_FR/sdk.js#xfbml=1&version=v2.0&appId=197983240245844";
        fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));
});