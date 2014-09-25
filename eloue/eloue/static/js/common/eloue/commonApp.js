"use strict";
define([
    "angular",
    "angular-cookies",
    "angular-resource",
    "angular-route",
    "datejs",
    "bootstrap-datepicker",
    "custom-scrollbar"
], function (angular) {
    // Create module
    return angular.module("EloueCommon", ["ngCookies", "ngResource", "ngRoute"]);
});
