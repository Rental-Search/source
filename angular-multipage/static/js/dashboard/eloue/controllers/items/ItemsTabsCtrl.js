"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the tabs on item details pages.
     */
    angular.module("EloueDashboardApp").controller("ItemsTabsCtrl", ["$scope", "$stateParams", function ($scope, $stateParams) {
        $scope.selectedItemId = $stateParams.id;
    }]);
});
