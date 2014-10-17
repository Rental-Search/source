"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the account's change password page.
     */
    angular.module("EloueDashboardApp").controller("AccountPasswordCtrl", [
        "$scope",
        "UsersService",
        function ($scope, UsersService) {
            $scope.markListItemAsSelected("account-part-", "account.password");
            $scope.resetPassword = function () {
                $scope.submitInProgress = true;
                if (!!$scope.currentUser) {
                    UsersService.resetPassword($scope.currentUser.id, $("#reset-password-form")).then(function(result) {
                        $scope.$apply(function () {
                            $scope.submitInProgress = false;
                        });
                    });
                }
            };
        }
    ]);
});