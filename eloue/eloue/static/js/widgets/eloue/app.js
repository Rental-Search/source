"use strict";
define([
    "angular",
    "angular-cookies",
    "angular-resource",
    "angular-route",
    "angular-ui-router",
    "eloue/modules/booking/BookingModule",
    "../../common/eloue/commonApp"
], function (angular) {
    // Create application module
    return angular.module("EloueApp", [
        "EloueCommon",
        "EloueApp.BookingModule",
        "ngCookies",
        "ngResource",
        "ngRoute",
        "ui.router",
        "localytics.directives"
    ]);
});
