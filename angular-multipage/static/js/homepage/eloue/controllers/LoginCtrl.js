define(["angular", "eloue/services/AuthService", "eloue/app"], function (angular) {
    "use strict";

    /**
     * Controller for the login form.
     */
    angular.module("EloueApp").controller("LoginCtrl", ["$scope", "AuthService", function ($scope, AuthService) {

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