define(["angular", "eloue/modules/user_management/services/AuthService", "eloue/modules/user_management/UserManagementModule"], function (angular) {
    "use strict";

    /**
     * Controller for the login form.
     */
    angular.module("EloueApp.UserManagementModule").controller("LoginCtrl", ["$scope", "AuthService", function ($scope, AuthService) {
        /**
         * User credentials.
         */
        $scope.credentials = {};

        /**
         * Sign in user.
         */
        $scope.login = function login() {
            AuthService.login($scope.credentials);
        };
    }]);
});