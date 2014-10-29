"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items shipping tab.
     */
    angular.module("EloueDashboardApp").controller("ItemsShippingCtrl", [
        "$scope",
        "$stateParams",
        "$timeout",
        "Endpoints",
        "ProductShippingPointsService",
        "ShippingPointsService",
        "UtilsService",
        function ($scope, $stateParams, $timeout, Endpoints, ProductShippingPointsService, ShippingPointsService, UtilsService) {
            $scope.markListItemAsSelected("item-tab-", "shipping");
            $scope.initCustomScrollbars();
            $scope.addressQuery = "";
            $scope.searchLat = "";
            $scope.searchLng = "";
            $scope.shippingPoints = [];
            $scope.showWellcome = false;
            $scope.showPointList = false;
            $scope.showPointDetails = false;
            $scope.selectedPointId = "";
            $scope.productsBaseUrl = Endpoints.api_url + "products/";
            $scope.productShippingPoint = {};

            ProductShippingPointsService.getByProduct($stateParams.id).then(function (data) {
                if (!!data.results && data.results.length > 0) {
                    $scope.productShippingPoint = data.results[0];
                    $scope.fillInSchedule($scope.productShippingPoint.opening_dates);
                    $scope.showPointDetails = true;
                } else {
                    $scope.showWellcome = true;
                }
            });

            $scope.currentUserPromise.then(function (currentUser) {
                $scope.currentUser = currentUser;
//                $scope.makeInitialSearchByAddress();
            });

            $scope.makeInitialSearchByAddress = function () {
                var location = false;
                if ($scope.showPointList && $scope.currentUser.default_address && $scope.currentUser.default_address.street && $scope.currentUser.default_address.city) {
                    $scope.addressQuery = $scope.currentUser.default_address.street + ", " + $scope.currentUser.default_address.city;
                    location = $scope.addressQuery;
                }
                $('#product-shipping-address').formmapper({
                    details: "form",
                    location: location
                });
                $scope.searchShippingPoints();
            };

            $scope.fillInSchedule = function (openingDates) {
                $scope.schedule = {};
                angular.forEach(openingDates, function (value, key) {
                    $scope.schedule[value.day_of_week] = $scope.filterTime(value.morning_opening_time) + " - "
                        + $scope.filterTime(value.morning_closing_time) + ", "
                        + $scope.filterTime(value.afternoon_opening_time) + " - "
                        + $scope.filterTime(value.afternoon_closing_time)
                });
            };

            $scope.filterTime = function (timeStr) {
                var parts = timeStr.split(":");
                return parts[0] + ":" + parts[1];
            };

            $scope.showMapPointList = function () {
                $scope.showWellcome = false;
                $scope.showPointList = true;
                $scope.showPointDetails = false;
                $scope.makeInitialSearchByAddress();
            };

            $scope.showMapPointDetails = function () {
                $scope.showWellcome = false;
                $scope.showPointList = false;
                $scope.showPointDetails = true;
            };

            $scope.showWellcomeScreen = function () {
                $scope.shippingPoints = [];
                $scope.showWellcome = true;
                $scope.showPointList = false;
                $scope.showPointDetails = false;
            };

            $scope.saveMapPoint = function () {
                $scope.submitInProgress = true;
                if (!!$scope.productShippingPoint && !!$scope.productShippingPoint.id) {
                    ProductShippingPointsService.deleteShippingPoint($scope.productShippingPoint.id).$promise.then(function (result) {
                        $scope.savePoint();
                    });
                } else {
                    $scope.savePoint();
                }
            };

            $scope.savePoint = function () {
                var selectedPoint = {};
                angular.forEach($scope.shippingPoints, function (value, key) {
                    if ($scope.selectedPointId == value.site_id) {
                        selectedPoint = value;
                    }
                });
                selectedPoint.product = $scope.productsBaseUrl + $stateParams.id + "/";
                selectedPoint.type = 1;
                ProductShippingPointsService.saveShippingPoint(selectedPoint).$promise.then(function (result) {
                    $scope.productShippingPoint = result;
                    $scope.submitInProgress = false;
                    $scope.fillInSchedule($scope.productShippingPoint.opening_dates);
                    $scope.showMapPointDetails();
                });
            };

            $scope.pointSelected = function (pointId) {
                $scope.selectedPointId = pointId;
            };

            $scope.cancelPointSelection = function () {
                $scope.showWellcomeScreen();
            };

            $scope.removeMapPoint = function () {
                ProductShippingPointsService.deleteShippingPoint($scope.productShippingPoint.id).$promise.then(function (result) {
                    $scope.productShippingPoint = {};
                    $scope.showWellcomeScreen();
                });
            };

            $scope.searchShippingPoints = function () {
                $timeout(function () {
                    var searchLat = $("#searchLat").attr("value"), searchLng = $("#searchLng").attr("value");
                    if (!!searchLat && !!searchLng) {
                        $scope.submitInProgress = true;
                        ShippingPointsService.searchDepartureShippingPointsByAddress($scope.addressQuery).then(function (data) {
                            $scope.shippingPoints = data;
                            $scope.submitInProgress = false;
                        });
                    }
                }, 500);
            };

        }]);
});
