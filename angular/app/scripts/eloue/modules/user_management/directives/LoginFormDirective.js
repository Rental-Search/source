/**
 * Created by mbaev on 09.07.2014.
 */
define(["angular", "eloue/modules/user_management/UserManagementModule", "eloue/modules/user_management/controllers/LoginCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display login form.
     */
    angular.module("EloueApp.UserManagementModule").directive("eloueLoginForm", [function () {
        return {
            restrict: "E",
            templateUrl: "/scripts/eloue/modules/user_management/views/login-form.html",
            scope: {},
            controller: "LoginCtrl"
        };
    }]);
    
});