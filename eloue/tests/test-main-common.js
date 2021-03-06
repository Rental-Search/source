var tests = [];
for (var file in window.__karma__.files) {
  if (window.__karma__.files.hasOwnProperty(file)) {
    if (/.spec\.js$/.test(file)) {
      tests.push(file);
    }
  }
}

requirejs.config({
    // Karma serves files from "/base"
    baseUrl: "/base/static/js/common",

    paths: {
        "bootstrap": "../../bower_components/bootstrap/dist/js/bootstrap.min",
        "underscore": "../../bower_components/lodash/dist/lodash.min",
        "jquery": "../../bower_components/jquery/dist/jquery.min",
        "angular": "../../bower_components/angular/angular.min",
        "angular-resource": "../../bower_components/angular-resource/angular-resource.min",
        "angular-cookies": "../../bower_components/angular-cookies/angular-cookies.min",
        "angular-mocks": "../../bower_components/angular-mocks/angular-mocks",
        "angular-sanitize": "../../bower_components/angular-sanitize/angular-sanitize.min",
        "angular-ui-router": "../../bower_components/angular-ui-router/release/angular-ui-router.min",
        "angular-i18n": "../../bower_components/angular-i18n/angular-locale_fr-fr",
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
        "angular": {"exports": "angular"},
        "angular-cookies": ["angular"],
        "angular-sanitize": ["angular"],
        "angular-resource": ["angular"],
        "angular-ui-router": ["angular"],
        "angular-i18n": ["angular"],
        "angular-translate": ["angular"],
        "angular-mocks": {
            deps: ["angular"],
            "exports": "angular.mock"
        },
        "jquery": {exports: "jquery"},
        "bootstrap": ["jquery"],
        "jquery-form": ["jquery"],
        "selectivizr": ["jquery"],
        "jquery-mousewheel": ["jquery"],
        "custom-scrollbar": ["jquery", "jquery-mousewheel"],
        "jquery-autosize": ["jquery"],
        "bootstrap-datepicker": ["jquery"],
        "bootstrap-datepicker-fr": ["jquery", "bootstrap-datepicker"],
        "chosen": ["jquery"],
        "toastr": ["jquery"],
        "formmapper": ["jquery"]
    },

    // ask Require.js to load these files (all our tests)
    deps: tests,

    // start test run, once Require.js is done
    callback: window.__karma__.start
});
