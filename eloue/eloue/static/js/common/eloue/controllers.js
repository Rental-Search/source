"use strict";
define(["../../common/eloue/commonApp"], function (EloueCommon) {

    /**
     * Controller for the login form.
     */
    EloueCommon.controller("LoginCtrl", ["$scope", "AuthService", function ($scope, AuthService) {
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

    /**
     * Controller for the registration form.
     */
    EloueCommon.controller("RegisterCtrl", ["$scope", "AuthService", function ($scope, AuthService) {

        /**
         * New user account data.
         */
        $scope.account = {};

        /**
         * Error occurred during registration.
         */
        $scope.registrationError = "";

        /**
         * Register new user in the system.
         */
        $scope.register = function register() {
            AuthService.register($scope.account).$promise.then(function(response) {
                // Sign in new user automatically
                var credentials = {
                    username: $scope.account.email,
                    password: $scope.account.password
                };
                AuthService.clearUserData();
                AuthService.login(credentials);
            }, function (error) {
                $scope.registrationError = error.data.detail;
            });
        };

        /**
         * Opens registration via email form.
         */
        $scope.openRegistrationForm = function openRegistrationForm() {
            var classic_form = $('.classic-form');
            classic_form.slideDown();
            $('.registration.email').slideUp();
        }
    }]);
});