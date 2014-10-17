"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items shipping tab.
     */
    angular.module("EloueDashboardApp").controller("ItemsShippingCtrl", [
        "$scope",
        "$stateParams",
        function ($scope, $stateParams) {
        	$scope.markListItemAsSelected("item-tab-", "shipping");
        	$scope.initCustomScrollbars();
        }]);
});
