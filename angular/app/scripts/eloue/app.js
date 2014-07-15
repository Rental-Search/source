"use strict";
define(["angular", "angular-cookies", "angular-resource", "angular-route", "eloue/modules/user_management/UserManagementModule",
    "eloue/modules/dashboard/DashboardModule", "eloue/modules/product_details/ProductDetailsModule"], function (angular) {
    // Create application module
    return angular.module("EloueApp", ["EloueApp.UserManagementModule", "EloueApp.DashboardModule", "EloueApp.ProductDetailsModule", "ngCookies", "ngResource", "ngRoute"]);
});
