define([
    "eloue/app",
    "../../../../common/eloue/services/UsersService"
], function (EloueDashboardApp) {
    "use strict";
    /**
     * Controller for the account's change password page.
     */
    EloueDashboardApp.controller("AccountPasswordCtrl", [
        "$scope",
        "$state",
        "$stateParams",
        "UsersService",
        "UtilsService",
        function ($scope, $state, $stateParams, UsersService, UtilsService) {
            $scope.markListItemAsSelected("account-part-", "account.password");

            $scope.errors = {
                current_password: "",
                password: "",
                confirm_password: ""
            };

            $scope.resetPassword = function () {
                $scope.submitInProgress = true;
                if ($scope.currentUser) {
                    UsersService.resetPassword($scope.currentUser.id, $("#reset-password-form")).then(function () {
                        $scope.submitInProgress = false;
                        $scope.showNotification('PERSONAL_INFO', 'update', true); 
                        $state.transitionTo($state.current, $stateParams, {reload: true});
                    }, function (error) {
                        if (!!error.responseJSON && !!error.responseJSON.errors) {
                            $scope.errors = {
                                current_password: error.responseJSON.errors.current_password ? error.responseJSON.errors.current_password[0] : "",
                                password: error.responseJSON.errors.password ? error.responseJSON.errors.password[0] : "",
                                confirm_password: error.responseJSON.errors.confirm_password ? error.responseJSON.errors.confirm_password[0] : ""
                            };
                        }
                        $scope.submitInProgress = false;
                        // Show generic error toastr only if there is no specific errors.
                        if (0 === $scope.errors.current_password.length && 0 === $scope.errors.password.length &&
                            0 === $scope.errors.confirm_password.length) {
                            $scope.showNotification("password", "reset", false);
                        }
                    });
                }
            };
        }
    ]);
});
