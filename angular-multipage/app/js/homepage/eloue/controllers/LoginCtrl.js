define(["angular", "eloue/services/AuthService", "eloue/app"], function (angular) {
    "use strict";

    angular.module("EloueApp").controller("LoginCtrl", ["$scope", "AuthService", function ($scope, AuthService) {
        $scope.credentials = {};

        /**
         * Sign in user.
         */
        $scope.login = function login() {
            AuthService.login($scope.credentials);
        };
    }]);
});