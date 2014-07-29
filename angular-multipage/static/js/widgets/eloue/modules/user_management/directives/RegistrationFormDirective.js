define(["angular", "eloue/modules/user_management/UserManagementModule", "eloue/modules/user_management/controllers/RegisterCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display registration form.
     */
    angular.module("EloueApp.UserManagementModule").directive("eloueRegistrationForm", ["$window", function ($window) {
        return {
            restrict: "E",
            templateUrl: $window.templatePrefix + "partials/homepage/registration-form.html",
            scope: {},
            controller: "RegisterCtrl"
        };
    }]);
});