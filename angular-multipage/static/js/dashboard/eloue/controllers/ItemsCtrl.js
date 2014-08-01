"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items page.
     */
    angular.module("EloueDashboardApp").controller("ItemsCtrl", ["$scope", function ($scope) {
        $scope.title = "Items title";
    }]);
});