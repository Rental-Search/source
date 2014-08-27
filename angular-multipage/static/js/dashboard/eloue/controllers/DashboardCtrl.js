"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the dashboard page.
     */
    angular.module("EloueDashboardApp").controller("DashboardCtrl", ["$scope", function ($scope) {
        $scope.currentUserPromise.then(function (currentUser) {
            // Save current user in the scope
            $scope.currentUser = currentUser;
            console.log($scope.currentUser);
        });
    }]);
});