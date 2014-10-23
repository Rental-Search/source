"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items shipping tab.
     */
    angular.module("EloueDashboardApp").controller("ItemsShippingCtrl", [
        "$scope",
        "$stateParams",
        "Endpoints",
        "ProductShippingPointsService",
        "ShippingPointsService",
        function ($scope, $stateParams, Endpoints, ProductShippingPointsService, ShippingPointsService) {
        	$scope.markListItemAsSelected("item-tab-", "shipping");
        	$scope.initCustomScrollbars();
            $scope.addressQuery = "";
            $scope.shippingPoints = [];
            $scope.showWellcome = false;
            $scope.showPointList = false;
            $scope.showPointDetails = false;
            $scope.selectedPointId = "";
            $scope.productsBaseUrl = Endpoints.api_url + "products/";
            $scope.productShippingPoint = {};

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
                $scope.submitInProgress = true;
                if (!!$scope.productShippingPoint && !!$scope.productShippingPoint.id) {
                    ProductShippingPointsService.deleteShippingPoint($scope.productShippingPoint.id).$promise.then(function(result) {
                        $scope.savePoint();
                    });
                } else {
                    $scope.savePoint();
                }
            };

            $scope.savePoint = function() {
                var selectedPoint = {};
                angular.forEach($scope.shippingPoints, function (value, key) {
                    if($scope.selectedPointId == value.site_id) {
                        selectedPoint = value;
                    }
                });
                selectedPoint.product = $scope.productsBaseUrl + $stateParams.id + "/";
                selectedPoint.type = 1;
                console.log(selectedPoint);
                ProductShippingPointsService.saveShippingPoint(selectedPoint).$promise.then(function(result) {
                    console.log(result);
                    $scope.productShippingPoint = result;
                    $scope.submitInProgress = false;
                    $scope.showMapPointDetails();
                });
            };

            $scope.pointSelected = function(pointId) {
                $scope.selectedPointId = pointId;
            };

            $scope.removeMapPoint = function() {
                ProductShippingPointsService.deleteShippingPoint($scope.productShippingPoint.id).$promise.then(function(result) {
                    $scope.productShippingPoint = {};
                    $scope.showMapPointList();
                });
            };

            $scope.searchShippingPoints = function() {
                if (!!$scope.addressQuery && $scope.addressQuery.length > 3) {
                    $scope.submitInProgress = true;
                    ShippingPointsService.searchDepartureShippingPointsByAddress($scope.addressQuery).then(function(data) {
                        $scope.shippingPoints = data;
                        $scope.submitInProgress = false;
                    });
                }
            }
        }]);
});
