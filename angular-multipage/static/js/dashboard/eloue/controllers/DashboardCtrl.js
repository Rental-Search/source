"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the dashboard page.
     */
    angular.module("EloueDashboardApp").controller("DashboardCtrl", ["$scope", function ($scope) {
        $scope.title = "Dashboard title";
    }]);
});