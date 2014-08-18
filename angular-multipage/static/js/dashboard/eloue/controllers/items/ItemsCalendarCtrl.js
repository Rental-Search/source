"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items calendar tab.
     */
    angular.module("EloueDashboardApp").controller("ItemsCalendarCtrl", ["$scope", function ($scope) {
        $scope.title = "Items calendar title";
    }]);
});