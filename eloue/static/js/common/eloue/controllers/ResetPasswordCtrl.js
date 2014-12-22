"use strict";
define([
    "../../../common/eloue/commonApp",
    "../../../common/eloue/services/AuthService"
], function (EloueCommon) {
    /**
     * Controller for the reset password form.
     */
    EloueCommon.controller("ResetPasswordCtrl", ["$scope", "$window", "AuthService", function ($scope, $window, AuthService) {

        $scope.passwdResetStage = true;
        $scope.passwdResetSuccess = false;
        $scope.resetPasswordError = null;

        $scope.sendResetRequest = function () {
            var form = $("#request-reset-password-form");
            AuthService.sendResetPasswordRequest(
                form,
                function (data) {
                    $scope.onSendResetRequestSuccess(data);
                },
                function (jqXHR) {
                    $scope.onSendResetRequestError(jqXHR);
                }
            );
        };

        $scope.onSendResetRequestSuccess = function (data) {
            $scope.$apply(function () {
                $scope.passwdResetStage = false;
            });
        };

        $scope.onSendResetRequestError = function (jqXHR) {
            var errorText = "";
            if (jqXHR.status == 400) {
                if (!!jqXHR.responseJSON.errors.email) {
                    errorText = jqXHR.responseJSON.errors.email[0];
                } else {
                    errorText = "Bad request.";
                }
            } else {
                errorText = "An error occured!";
            }
            $scope.$apply(function () {
                $scope.resetPasswordError = errorText;
            });
        };

        $scope.resetPassword = function () {
            var form = $("#reset-password-form");
            AuthService.resetPassword(
                form,
                $window.location,
                function (data) {
                    $scope.onResetPasswordSuccess(data);
                },
                function (jqXHR) {
                    $scope.onResetPasswordError(jqXHR);
                }
            );
        };

        $scope.onResetPasswordSuccess = function (data) {
            $scope.$apply(function () {
                $scope.passwdResetSuccess = true;
            });
        };

        $scope.onResetPasswordError = function (jqXHR) {
            var errorText = "";
            if (jqXHR.status == 400) {
                if (!!jqXHR.responseJSON.errors.__all__) {
                    errorText = jqXHR.responseJSON.errors.__all__[0];
                } else {
                    errorText = "Bad request.";
                }
            } else {
                errorText = "An error occured!";
            }
            $scope.$apply(function () {
                $scope.resetPasswordError = errorText;
            });
        };

        $("#reset-password-confirm").modal("show");
    }]);
});
