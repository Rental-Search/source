"use strict";

define(["angular", "eloue/app", "../../../../common/eloue/services"], function (angular) {

    /**
     * Controller for the account's profile page.
     */
    angular.module("EloueDashboardApp").controller("AccountProfileCtrl", [
        "$scope",
        "UsersService",
        function ($scope, UsersService) {
            $scope.currentUserPromise.then(function (currentUser) {
                // Save current user in the scope
                $scope.currentUser = currentUser;
            });

            // Send form when a file changes
            $scope.onFileChanged = function () {
                UsersService.sendForm($scope.currentUser.id, $("#change-photo"), function (data) {
                    $scope.$apply(function () {
                        $scope.currentUser = data;
                    });
                });
            };

            // Send form with data by submit
            $scope.dataFormSubmit = function () {
                UsersService.sendForm($scope.currentUser.id, $("#profile-information"));
            };
        }
    ]);
});