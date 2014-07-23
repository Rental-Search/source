define(["angular", "eloue/modules/user_management/UserManagementModule", "eloue/services"], function (angular) {
    "use strict";

    angular.module("EloueApp.UserManagementModule").controller("RegisterCtrl", ["$scope", "Users", function ($scope, Users) {
        $scope.account = {};

        /**
         * Register new user in the system.
         */
        $scope.register = function register() {
            Users.register($scope.account, function (response, header) {
//                $rootScope.$broadcast("redirectToLogin");
            });
        };

        $scope.openRegistrationForm = function openRegistrationForm() {
            var classic_form = $('.classic-form');
//            console.log(classic_form);
//            classic_form.hide();
//            $('.registration.email').on('click', function(){
                classic_form.slideDown();
                $('.registration.email').slideUp();
//            });
        }

    }]);
});
