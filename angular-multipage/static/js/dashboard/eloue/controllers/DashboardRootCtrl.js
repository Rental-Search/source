"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Root controller for the dashboard app.
     */
    angular.module("EloueDashboardApp").controller("DashboardRootCtrl", [
        "$scope",
        "$cookies",
        function ($scope, $cookies) {
            // Read authorization token
            $scope.currentUserToken = $cookies.user_token;

            // Set jQuery ajax interceptors
            $.ajaxSetup({
                beforeSend: function (jqXHR) {
                    if (!!$scope.currentUserToken) {
                        jqXHR.setRequestHeader("authorization", "Bearer " + $scope.currentUserToken);
                    }
                }
            });
        }
    ]);
});