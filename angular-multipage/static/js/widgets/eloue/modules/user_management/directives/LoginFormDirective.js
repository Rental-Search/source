define(["angular", "eloue/modules/user_management/UserManagementModule", "eloue/modules/user_management/controllers/LoginCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display login form.
     */
    angular.module("EloueApp.UserManagementModule").directive("eloueLoginForm", ["$window", function ($window) {
        return {
            restrict: "E",
            templateUrl: $window.templatePrefix + "partials/homepage/login-form.html",
            scope: {},
            controller: "LoginCtrl"
        };
    }]);
});