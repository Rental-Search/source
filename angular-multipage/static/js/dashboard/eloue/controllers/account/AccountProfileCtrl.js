"use strict";

define(["angular", "eloue/app", "../../../../common/eloue/services"], function (angular) {

    /**
     * Controller for the account's profile page.
     */
    angular.module("EloueDashboardApp").controller("AccountProfileCtrl", [
        "$scope",
        "UsersService",
        function ($scope, UsersService) {
            UsersService.getMe(function (currentUser) {
                $scope.currentUser = currentUser;

                $scope.submit = function () {
                    var context = $("#profile_form");

                    var textFields = $(":text", context);
                    var fileFields = $(":file", context);

                    UsersService.sendFormData($scope.currentUser.id, textFields, fileFields);
                };
            });
        }
    ]);
});