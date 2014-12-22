"use strict";

define([
    "eloue/app",
    "../../../../common/eloue/services/UsersService"
], function (EloueDashboardApp) {

    /**
     * Controller for the account's change password page.
     */
    EloueDashboardApp.controller("AccountPasswordCtrl", [
        "$scope",
        "$state",
        "$stateParams",
        "UsersService",
        function ($scope, $state, $stateParams, UsersService) {
            $scope.markListItemAsSelected("account-part-", "account.password");

            $scope.errors = {
                current_password: "",
                password: "",
                confirm_password: ""
            };

            $scope.resetPassword = function () {
                $scope.submitInProgress = true;
                if (!!$scope.currentUser) {
                    UsersService.resetPassword($scope.currentUser.id, $("#reset-password-form")).then(function (result) {
                        $scope.submitInProgress = false;
                        $scope.showNotification("password", "reset", true);
                        $state.transitionTo($state.current, $stateParams, {reload: true});
                    }, function (error) {
                        if (!!error.responseJSON && !!error.responseJSON.errors) {
                            $scope.errors = {
                                current_password: !!error.responseJSON.errors.current_password ? error.responseJSON.errors.current_password[0] : "",
                                password: !!error.responseJSON.errors.password ? error.responseJSON.errors.password[0] : "",
                                confirm_password: !!error.responseJSON.errors.confirm_password ? error.responseJSON.errors.confirm_password[0] : ""
                            };
                        }
                        $scope.submitInProgress = false;
                        $scope.showNotification("password", "reset", false);
                    });
                }
            };
        }
    ]);
});
