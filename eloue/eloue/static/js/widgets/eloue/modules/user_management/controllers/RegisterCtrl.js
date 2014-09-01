define(["angular", "eloue/modules/user_management/services/AuthService", "eloue/modules/user_management/UserManagementModule"], function (angular) {
    "use strict";

    /**
     * Controller for the registration form.
     */
    angular.module("EloueApp.UserManagementModule").controller("RegisterCtrl", ["$scope", "AuthService", function ($scope, AuthService) {

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
