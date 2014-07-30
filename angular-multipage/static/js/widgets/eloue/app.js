"use strict";
define(["angular", "angular-cookies", "angular-resource", "angular-route", "eloue/modules/user_management/UserManagementModule",
     "eloue/modules/booking/BookingModule", "../../common/eloue/commonApp"], function (angular) {
    // Create application module
    return angular.module("EloueApp", ["EloueCommon", "EloueApp.UserManagementModule", "EloueApp.BookingModule", "ngCookies", "ngResource", "ngRoute"]);
});
