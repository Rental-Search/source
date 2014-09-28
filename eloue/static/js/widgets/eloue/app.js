"use strict";
define([
    "angular",
    "angular-cookies",
    "angular-resource",
    "angular-route",
    "eloue/modules/booking/BookingModule",
    "../../common/eloue/commonApp"
], function (angular) {
    // Create application module
    return angular.module("EloueApp", [
        "EloueCommon",
        "EloueApp.BookingModule",
        "ngCookies",
        "ngResource",
        "ngRoute"
    ]);
});
