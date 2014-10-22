"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items shipping tab.
     */
    angular.module("EloueDashboardApp").controller("ItemsShippingCtrl", [
        "$scope",
        "$stateParams",
        "ProductShippingPointsService",
        "ShippingPointsService",
        function ($scope, $stateParams, ProductShippingPointsService, ShippingPointsService) {
        	$scope.markListItemAsSelected("item-tab-", "shipping");
        	$scope.initCustomScrollbars();
            $scope.addressQuery = "";
            $scope.shippingPoints = [];
            $scope.showWellcome = false;
            $scope.showPointList = false;
            $scope.showPointDetails = false;

            ProductShippingPointsService.getByProduct($stateParams.id).then(function(data) {
                console.log(data);
                if (!!data.results && data.results.length > 0) {
                    $scope.productShippingPoint = data.results[0];
                    $scope.showPointDetails = true;
                } else {
                    $scope.showWellcome = true;
                }
            });

            $scope.showMapPointList = function() {
                $scope.showWellcome = false;
                $scope.showPointList = true;
                $scope.showPointDetails = false;
            };

            $scope.showMapPointDetails = function() {
                $scope.showWellcome = false;
                $scope.showPointList = false;
                $scope.showPointDetails = true;
            };

            $scope.saveMapPoint = function() {
                //TODO: save selected
                $scope.showMapPointDetails();
            };

            $scope.removeMapPoint = function() {
                //TODO: remove point
                $scope.showMapPointList();
            };

            $scope.searchShippingPoints = function() {
                if (!!$scope.addressQuery && $scope.addressQuery.length > 3) {
                    ShippingPointsService.searchDepartureShippingPointsByAddress($scope.addressQuery).then(function(data) {
                        console.log(data);
                        $scope.shippingPoints = data.results;
                    });
                }
            }
        }]);
});
