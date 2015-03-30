({
    mainConfigFile: "main.js",
    baseUrl: "./",
    paths: {
        "bootstrap": "../../bower_components/bootstrap/dist/js/bootstrap",
        "underscore": "../../bower_components/lodash/dist/lodash",
        "jQuery": "../../bower_components/jquery/dist/jquery",
        "angular": "../../bower_components/angular/angular",
        "angular-resource": "../../bower_components/angular-resource/angular-resource",
        "angular-cookies": "../../bower_components/angular-cookies/angular-cookies",
        "angular-sanitize": "../../bower_components/angular-sanitize/angular-sanitize",
        "angular-ui-router": "../../bower_components/angular-ui-router/release/angular-ui-router",
        "angular-translate": "../../bower_components/angular-translate/angular-translate",
        "bootstrap-datepicker": "../../bower_components/bootstrap-datepicker/js/bootstrap-datepicker",
        "bootstrap-datepicker-fr": "../../bower_components/bootstrap-datepicker/js/locales/bootstrap-datepicker.fr",
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
        "formmapper": ["jQuery"],
        "angular-cookie": ["angular"]
    },
    removeCombined: true,
    findNestedDependencies: true,
    name: "main"
})