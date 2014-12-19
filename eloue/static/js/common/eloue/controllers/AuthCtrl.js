"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Root controller for pages which content depends on user authorized (e.g. Home page).
     */
    EloueCommon.controller("AuthCtrl", [
        "$scope",
        "$window",
        "AuthService",
        "UsersService",
        function ($scope, $window, AuthService, UsersService) {
            var currentUserToken = AuthService.getCookie("user_token");
            if (currentUserToken) {
                // Get current user
                $scope.currentUserPromise = UsersService.getMe().$promise;
                $scope.currentUserPromise.then(function (currentUser) {
                    // Save current user in the scope
                    $scope.currentUser = currentUser;
                    UsersService.getStatistics($scope.currentUser.id).$promise.then(function (stats) {
                        $scope.userStats = stats;
                    });
                });
            }

            $scope.logout = function () {
                AuthService.clearUserData();
                if ($window.location.href.indexOf("dashboard") !== -1) {
                    $window.location.href = "/";
                } else {
                    $window.location.reload();
                }
            };
        }]);
});
