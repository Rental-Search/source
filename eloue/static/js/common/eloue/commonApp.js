"use strict";
define([
    "angular",
    "angular-cookies",
    "angular-cookie",
    "angular-resource",
    "angular-translate",
    "angular-translate-interpolation-messageformat",
    "datejs",
    "chosen",
    "bootstrap-datepicker",
    "bootstrap-datepicker-fr",
    "jquery-mousewheel",
    "custom-scrollbar",
    "filesaver"
], function (angular) {
    // Create module
    return angular.module("EloueCommon", ["ngCookies", "ngResource"]);
});
