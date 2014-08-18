"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items photos and info page.
     */
    angular.module("EloueDashboardApp").controller("ItemsInfoCtrl", ["$scope", function ($scope) {
        $scope.title = "Items info title";
    }]);
});
