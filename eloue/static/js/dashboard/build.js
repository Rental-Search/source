({
    mainConfigFile: "main.js",
    baseUrl: "./",
    paths: {
        "bootstrap": "../../bower_components/bootstrap/dist/js/bootstrap",
        "underscore": "../../bower_components/lodash/lodash",
        "jquery": "../../bower_components/jquery/dist/jquery",
        "angular": "../../bower_components/angular/angular",
        "angular-resource": "../../bower_components/angular-resource/angular-resource",
        "angular-cookies": "../../bower_components/angular-cookies/angular-cookies",
        "angular-sanitize": "../../bower_components/angular-sanitize/angular-sanitize",
        "angular-ui-router": "../../bower_components/angular-ui-router/release/angular-ui-router",
        "angular-translate": "../../bower_components/angular-translate/angular-translate",
        "angular-translate-interpolation-messageformat": "../../bower_components/angular-translate-interpolation-messageformat/angular-translate-interpolation-messageformat",
        "messageformat": "../../bower_components/messageformat/messageformat",
        "angular-moment": "../../bower_components/angular-moment/angular-moment",
        "moment": "../../bower_components/moment/min/moment-with-locales",
        "bootstrap-datepicker": "../../bower_components/bootstrap-datepicker/dist/js/bootstrap-datepicker",
        // "bootstrap-datepicker-fr": "../../bower_components/bootstrap-datepicker/dist/locales/bootstrap-datepicker.fr.min",
        "jquery-form": "../../bower_components/jquery-form/jquery.form",
        "datejs": "../../bower_components/datejs/build/date",
        "chosen": "../../bower_components/chosen/chosen.jquery",
        "selectivizr": "../../bower_components/selectivizr/selectivizr",
        "jquery-mousewheel": "../../bower_components/jquery-mousewheel/jquery.mousewheel",
        "custom-scrollbar": "../../bower_components/malihu-custom-scrollbar-plugin/jquery.mCustomScrollbar",
        "jquery-autosize": "../../bower_components/jquery-autosize/jquery.autosize",
        "toastr": "../../bower_components/toastr/toastr",
        "formmapper": "../formmapper",
        "filesaver": "../FileSaver.min",
        "angular-cookie": "../../bower_components/angular-cookie/angular-cookie"
    },
    shim: {
        "angular": {
            deps: ["jquery"],
            "exports": "angular"
        },
        "angular-cookies": ["angular"],
        "angular-sanitize": ["angular"],
        "angular-resource": ["angular"],
        "angular-ui-router": ["angular"],
        "angular-translate": ["angular"],
        "angular-translate-interpolation-messageformat": {
            deps: ["angular-translate", "messageformat"],
            init: function (angular, MessageFormat) {
                this.MessageFormat = MessageFormat;
            }
        },
        "angular-mocks": {
            deps: ["angular"],
            "exports": "angular.mock"
        },
        // "bootstrap-datepicker-fr":["jquery", "bootstrap-datepicker"],
        "bootstrap": ["jquery"],
        "jquery-form": ["jquery"],
        "selectivizr": ["jquery"],
        "jquery-mousewheel": ["jquery"],
        "custom-scrollbar": ["jquery", "jquery-mousewheel"],
        "jquery-autosize": ["jquery"],
        "chosen": ["jquery"],
        "toastr": ["jquery"],
        "formmapper": ["jquery"],
        "angular-cookie": ["angular"]
    },
    removeCombined: true,
    findNestedDependencies: true,
    name: "main"
})