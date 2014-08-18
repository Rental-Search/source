"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the account page.
     */
    angular.module("EloueDashboardApp").controller("AccountCtrl", [
        "$scope",
        "UsersService",
        function ($scope, UsersService) {
            UsersService.getMe().$promise.then(function (currentUser) {
                $scope.currentUser = currentUser;
            });
        }
    ]);
});