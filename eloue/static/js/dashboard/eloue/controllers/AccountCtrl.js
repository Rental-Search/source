"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the account page.
     */
    angular.module("EloueDashboardApp").controller("AccountCtrl", [
        "$scope",
        "$state",
        "UsersService",
        function ($scope, $state, UsersService) {
            UsersService.getMe().$promise.then(function (currentUser) {
                $scope.currentUser = currentUser;
                if ($state.current.name == "account") {
                    $state.go("account.profile");
                }
            });
        }
    ]);
});