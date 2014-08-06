"use strict";

define(["angular", "eloue/app", "../../../../common/eloue/services"], function (angular) {

    /**
     * Controller for the account's profile page.
     */
    angular.module("EloueDashboardApp").controller("AccountProfileCtrl", [
        "$scope",
        "UsersService",
        "Endpoints",
        function ($scope, UsersService, Endpoints) {
            UsersService.getMe(function (currentUser) {
                // Save current user in the scope
                $scope.currentUser = currentUser;

                // Send form by submit
                $scope.submit = function () {
                    UsersService.sendForm($scope.currentUser.id, $("#profile_form"), function (data) {
                        $scope.currentUser = data;
                    });
                };
            });
        }
    ]);
});