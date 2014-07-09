define(["angular", "eloue/modules/user_management/services/AuthService", "eloue/modules/user_management/UserManagementModule"], function (angular) {
    "use strict";

    angular.module("EloueApp.UserManagementModule").controller("LoginCtrl", ["$scope", "AuthService", function ($scope, AuthService) {
        $scope.credentials = {};

        /**
         * Sign in user.
         */
        $scope.login = function login() {
            AuthService.login($scope.credentials);
        };
    }]);
});