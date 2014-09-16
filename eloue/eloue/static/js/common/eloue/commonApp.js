"use strict";
define([
    "angular",
    "angular-cookies",
    "angular-resource",
    "angular-route",
    "bootstrap-datepicker",
    "custom-scrollbar"
], function (angular) {
    // Create module
    return angular.module("EloueCommon", ["ngCookies", "ngResource", "ngRoute"]);
});
