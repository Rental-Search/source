/**
 * Created by mbaev on 09.07.2014.
 */
define(["angular", "eloue/modules/user_management/UserManagementModule", "eloue/modules/user_management/controllers/RegisterCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display registration form.
     */
    angular.module("EloueApp.UserManagementModule").directive("eloueRegistrationForm", [function () {
        return {
            restrict: "E",
            templateUrl: "/scripts/eloue/modules/user_management/views/registration-form.html",
            scope: {},
            controller: "RegisterCtrl"
        };
    }]);
});