"use strict";
define([
    "angular",
    "angular-cookies",
    "angular-resource",
    "angular-route",
    "datejs",
    "chosen",
    "bootstrap-datepicker",
    "bootstrap-datepicker-fr",
    "jquery-mousewheel",
    "custom-scrollbar",
    "filesaver"
], function (angular) {
    // Create module
    return angular.module("EloueCommon", ["ngCookies", "ngResource", "ngRoute"]);
});
