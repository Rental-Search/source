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
         * Register new user in the system.
         */
        $scope.register = function register() {
            AuthService.register($scope.account);
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
