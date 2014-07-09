"use strict";
define(["angular", "angular-cookies", "angular-resource", "angular-route", "eloue/modules/user_management/UserManagementModule", "eloue/modules/dashboard/DashboardModule"], function (angular) {
    // Create application module
    return angular.module("EloueApp", ["EloueApp.UserManagementModule", "EloueApp.DashboardModule", "ngCookies", "ngResource", "ngRoute"]);
});
