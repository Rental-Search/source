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
        }]);
});
