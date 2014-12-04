// Karma configuration
// http://karma-runner.github.io/0.10/config/configuration-file.html

module.exports = function (config) {
    config.set({
        // base path, that will be used to resolve files and exclude
        basePath: '',

        // testing framework to use (jasmine/mocha/qunit/...)
        frameworks: ['jasmine', 'requirejs'],

        // list of files / patterns to load in the browser
        files: [
            {pattern: 'static/bower_components/bootstrap/dist/js/bootstrap.js', included: false },
            {pattern: 'static/bower_components/lodash/dist/lodash.js', included: false },
            {pattern: 'static//bower_components/jquery/dist/jquery.js', included: false },
            {pattern: 'static/bower_components/jqueryui/jquery-ui.js', included: false },
            {pattern: 'static/bower_components/jqueryui/ui/core.js', included: false },
            {pattern: 'static/bower_components/jqueryui/ui/mouse.js', included: false },
            {pattern: 'static/bower_components/jqueryui/ui/widget.js', included: false },
            {pattern: 'static/bower_components/angular/angular.js', included: false },
            {pattern: 'static/bower_components/angular-mocks/angular-mocks.js', included: false },
            {pattern: 'static/bower_components/angular-resource/angular-resource.js', included: false },
            {pattern: 'static/bower_components/angular-route/angular-route.js', included: false },
            {pattern: 'static/bower_components/angular-cookies/angular-cookies.js', included: false },
            {pattern: 'static/bower_components/angular-sanitize/angular-sanitize.js', included: false },
            {pattern: 'static/bower_components/angular-i18n/angular-locale_fr-fr.js', included: false },
            {pattern: 'static/bower_components/angular-translate/angular-translate.min.js', included: false },
            {pattern: 'static/bower_components/moment/moment.js', included: false },
            {pattern: 'static/bower_components/angular-moment/angular-moment.js', included: false },
            {pattern: 'static/bower_components/bootstrap-datepicker/js/bootstrap-datepicker.js', included: false },
            {pattern: 'static/bower_components/bootstrap-datepicker/js/locales/bootstrap-datepicker.fr.js', included: false },
            {pattern: 'static/bower_components/jquery-form/jquery.form.js', included: false },
            {pattern: 'static/bower_components/datejs/build/date.js', included: false },
            {pattern: 'static/bower_components/chosen/chosen.jquery.js', included: false },
            {pattern: 'static/bower_components/html5shiv/dist/html5shiv.js', included: false },
            {pattern: 'static/bower_components/respond/respond.src.js', included: false },
            {pattern: 'static/bower_components/placeholders/lib/utils.js', included: false },
            {pattern: 'static/bower_components/placeholders/lib/main.js', included: false },
            {pattern: 'static/bower_components/placeholders/lib/adapters/placeholders.jquery.js', included: false },
            {pattern: 'static/bower_components/malihu-custom-scrollbar-plugin/jquery.mCustomScrollbar.js', included: false },
            {pattern: 'static/bower_components/jquery-mousewheel/jquery.mousewheel.js', included: false },
            {pattern: 'static/bower_components/toastr/toastr.js', included: false },
            {pattern: 'static/js/*.js', included: false },
            {pattern: 'static/js/**/*.js', included: false },
            {pattern: 'tests/unit/widgets/**/*.js', included: false },
            'tests/test-main-widgets.js'
        ],

        // list of files / patterns to exclude
        exclude: [
            'static/js/dashboard/main.js',
            'static/js/widgets/main.js'
        ],

        // web server port
        port: 8080,

        // level of logging
        // possible values: LOG_DISABLE || LOG_ERROR || LOG_WARN || LOG_INFO || LOG_DEBUG
        logLevel: config.LOG_DEBUG,


        // enable / disable watching file and executing tests whenever any file changes
        autoWatch: false,


        // Start these browsers, currently available:
        // - Chrome
        // - ChromeCanary
        // - Firefox
        // - Opera
        // - Safari (only Mac)
        // - PhantomJS
        // - IE (only Windows)
        browsers: ['PhantomJS'],


        // Continuous Integration mode
        // if true, it capture browsers, run tests and exit
        singleRun: true
    });
};
