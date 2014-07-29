define(["angular", "eloue/modules/user_management/UserManagementModule", "eloue/resources"], function (angular) {
    "use strict";

    /**
     * Controller for the registration form.
     */
    angular.module("EloueApp.UserManagementModule").controller("RegisterCtrl", ["$scope", "Users", function ($scope, Users) {

        /**
         * New user account data.
         */
        $scope.account = {};

        /**
         * Register new user in the system.
         */
        $scope.register = function register() {
            Users.register($scope.account, function (response, header) {
                //TODO: define logic after user successfully registered
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
