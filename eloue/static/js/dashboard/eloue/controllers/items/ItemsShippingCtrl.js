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
        "UtilsService",
        function ($scope, $stateParams, Endpoints, ProductShippingPointsService, ShippingPointsService, UtilsService) {
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
                if (!!data.results && data.results.length > 0) {
                    $scope.productShippingPoint = data.results[0];
                    $scope.fillInSchedule($scope.productShippingPoint.opening_dates);
                    $scope.showPointDetails = true;
                } else {
                    $scope.showWellcome = true;
                }
            });

            $scope.fillInSchedule = function(openingDates) {
                console.log(openingDates);
                $scope.schedule = {};
                angular.forEach(openingDates, function (value, key) {
                    $scope.schedule[value.day_of_week] = UtilsService.formatDate(value.morning_opening_time, "HH:mm") + " - "
                        + UtilsService.formatDate(value.morning_closing_time, "HH:mm") + ", "
                        + UtilsService.formatDate(value.afternoon_opening_time, "HH:mm") + " - "
                        + UtilsService.formatDate(value.afternoon_closing_time, "HH:mm")
                });
            };

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
                ProductShippingPointsService.saveShippingPoint(selectedPoint).$promise.then(function(result) {
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
                    $scope.fillInSchedule($scope.productShippingPoint.opening_dates);
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
