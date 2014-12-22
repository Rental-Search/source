"use strict";

define([
    "eloue/app",
    "../../../common/eloue/services/UsersService"
], function (EloueDashboardApp) {

    /**
     * Controller for the account page.
     */
    EloueDashboardApp.controller("AccountCtrl", [
        "$scope",
        "$state",
        "UsersService",
        function ($scope, $state, UsersService) {
            UsersService.getMe().$promise.then(function (currentUser) {
                $scope.currentUser = currentUser;
                // When user clicks on account dashboard tab he should be redirected to profile page.
                if ($state.current.name == "account") {
                    $state.go("account.profile");
                }
            });
        }
    ]);
});
