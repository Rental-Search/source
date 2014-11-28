var tests = [];
for (var file in window.__karma__.files) {
  if (window.__karma__.files.hasOwnProperty(file)) {
    if (/.spec\.js$/.test(file)) {
      tests.push(file);
    }
  }
}

requirejs.config({
    // Karma serves files from '/base'
    baseUrl: '/base/static/js/widgets',

    paths: {
        "bootstrap": "../../bower_components/bootstrap/dist/js/bootstrap",
        "lodash": "../../bower_components/lodash/dist/lodash",
        "jQuery": "../../bower_components/jquery/dist/jquery",
        "jquery-ui": "../../bower_components/jqueryui/jquery-ui",
        "jshashtable": "../jshashtable-2.1_src",
        "jquery.numberformatter": "../jquery.numberformatter-1.2.3",
        "tmpl": "../tmpl",
        "jquery.dependClass": "../jquery.dependClass-0.1",
        "draggable": "../draggable-0.1",
        "slider": "../jquery.slider",
        "core": "../../bower_components/jqueryui/ui/core",
        "mouse": "../../bower_components/jqueryui/ui/mouse",
        "widget": "../../bower_components/jqueryui/ui/widget",
        "angular": "../../bower_components/angular/angular",
        "angular-resource": "../../bower_components/angular-resource/angular-resource",
        "angular-cookies": "../../bower_components/angular-cookies/angular-cookies",
        "angular-sanitize": "../../bower_components/angular-sanitize/angular-sanitize",
        "angular-mocks": "../../bower_components/angular-mocks/angular-mocks",
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
        "formmapper": "../formmapper"
    },

    shim: {
        "angular": {"exports": "angular"},
        "angular-cookies": ["angular"],
        "angular-sanitize": ["angular"],
        "angular-resource": ["angular"],
        "angular-moment": ["angular"],
        "angular-mocks": {
            deps: ["angular"],
            "exports": "angular.mock"
        },
        "jQuery": {exports: "jQuery"},
        "jquery-ui": ["jQuery"],
        "jshashtable": ["jQuery"],
        "jquery.numberformatter": ["jQuery"],
        "tmpl": ["jQuery"],
        "jquery.dependClass": ["jQuery"],
        "draggable": ["jQuery"],
        "slider": ["jQuery"],
        "core": ["jQuery"],
        "mouse": ["jQuery"],
        "widget": ["jQuery"],
        "bootstrap": ["jQuery"],
        "jquery-form": ["jQuery"],
        "moment": ["jQuery"],
        "bootstrap-datepicker": ["jQuery"],
        "bootstrap-datepicker-fr": ["jQuery", "bootstrap-datepicker"],
        "chosen": ["jQuery"],
        "placeholders-jquery": ["jQuery"],
        "formmapper": ["jQuery"],
        "jquery-mousewheel": ["jQuery"],
        "custom-scrollbar": ["jQuery", "jquery-mousewheel"],
        "toastr": ["jQuery"]
    },

    // ask Require.js to load these files (all our tests)
    deps: tests,

    // start test run, once Require.js is done
    callback: window.__karma__.start
});
