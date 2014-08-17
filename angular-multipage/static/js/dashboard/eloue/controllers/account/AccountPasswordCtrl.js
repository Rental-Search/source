"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the account's change password page.
     */
    angular.module("EloueDashboardApp").controller("AccountPasswordCtrl", [
        "$scope",
        "UsersService",
        function ($scope, UsersService) {
            $scope.resetPassword = function () {
                UsersService.resetPassword($("#reset-password-form"));
            };
        }
    ]);
});