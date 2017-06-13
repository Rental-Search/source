define([
    "../../../common/eloue/commonApp",
    "../../../common/eloue/services/AuthService",
    "../../../common/eloue/services/UsersService"
], function (EloueCommon) {
    "use strict";
    /**
     * Root controller for pages which content depends on user authorized (e.g. Home page).
     */
    EloueCommon.controller("AuthCtrl", [
        "$scope",
        "$window",
        "$document",
        "AuthService",
        "UsersService",
        function ($scope, $window, $document, AuthService, UsersService) {
            var currentUserToken = AuthService.getUserToken();
            if (currentUserToken) {
                // Get current user
                $scope.currentUserPromise = UsersService.getMe();
                $scope.currentUserPromise.then(function (currentUser) {
                    // Save current user in the scope
                    $scope.currentUser = currentUser;
                    UsersService.getStatistics($scope.currentUser.id).then(function (stats) {
                        $scope.userStats = stats;
                    });
                });
            }

            $scope.logout = function () {
                AuthService.clearUserData();
                analytics.track('Logged Out');
                if ($window.location.href.indexOf("dashboard") !== -1) {
                    $window.location.href = "/";
                } else {
                    $window.location.reload();
                }
            };

            (function (d, s, id) {
                var js, fjs = d.getElementsByTagName(s)[0];
                if (d.getElementById(id)) {
                    return;
                }
                js = d.createElement(s);
                js.id = id;
                js.src = "//connect.facebook.net/fr_FR/sdk.js#xfbml=1&version=v2.0&appId=197983240245844";
                fjs.parentNode.insertBefore(js, fjs);
            }($document[0], "script", "facebook-jssdk"));
        }]);
});
