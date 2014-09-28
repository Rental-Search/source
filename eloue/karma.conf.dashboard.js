// Karma configuration
// http://karma-runner.github.io/0.10/config/configuration-file.html

module.exports = function(config) {
  config.set({
    // base path, that will be used to resolve files and exclude
    basePath: '',

    // testing framework to use (jasmine/mocha/qunit/...)
    frameworks: ['jasmine', 'requirejs'],

    // list of files / patterns to load in the browser
    files: [
      {pattern: 'static/bower_components/bootstrap/dist/js/bootstrap.min.js', included: false },
      {pattern: 'static/bower_components/jquery/dist/jquery.min.js', included: false },
      {pattern: 'static/bower_components/bootstrap-datepicker/js/bootstrap-datepicker.js', included: false },
      {pattern: 'static/bower_components/angular/angular.min.js', included: false },
      {pattern: 'static/bower_components/angular-mocks/angular-mocks.js', included: false },
      {pattern: 'static/bower_components/angular-resource/angular-resource.min.js', included: false },
      {pattern: 'static/bower_components/angular-cookies/angular-cookies.min.js', included: false },
      {pattern: 'static/bower_components/angular-sanitize/angular-sanitize.min.js', included: false },
      {pattern: 'static/bower_components/angular-route/angular-route.min.js', included: false },
      {pattern: 'static/bower_components/datejs/build/production/date.min.js', included: false },
      {pattern: 'static/bower_components/angular-ui-router/release/angular-ui-router.min.js', included: false },
      {pattern: 'static/bower_components/angular-translate/angular-translate.min.js', included: false },
      {pattern: 'static/bower_components/jquery-form/jquery.form.js', included: false },
      {pattern: 'static/bower_components/selectivizr/selectivizr.js', included: false },
      {pattern: 'static/bower_components/jquery-autosize/jquery.autosize.min.js', included: false },
      {pattern: 'static/bower_components/jquery-mousewheel/jquery.mousewheel.js', included: false },
      {pattern: 'static/bower_components/malihu-custom-scrollbar-plugin/jquery.mCustomScrollbar.js', included: false },
      {pattern: 'static/bower_components/toastr/toastr.min.js', included: false },
      {pattern: 'static/js/*.js', included: false },
      {pattern: 'static/js/**/*.js', included: false },
      {pattern: 'tests/unit/dashboard/**/*.js', included: false },
      'tests/test-main-dashboard.js'
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
    browsers: ['Chrome'],
//      plugins: ['karma-coverage'],
//      reporters: ['progress', 'coverage'],
//      preprocessors: {
//          // source files, that you wanna generate coverage for
//          // do not include tests or libraries
//          // (these files will be instrumented by Istanbul)
//          'static/js/**/*.js': ['coverage']
//      },
    // Continuous Integration mode
    // if true, it capture browsers, run tests and exit
    singleRun: false
  });
};
