define([
    "eloue/app",
    "../../../../common/eloue/values",
    "../../../../common/eloue/services/ProductsService",
    "../../../../common/eloue/services/ProductShippingPointsService",
    "../../../../common/eloue/services/ShippingPointsService",
    "../../../../common/eloue/services/UsersService"
], function (EloueDashboardApp) {
    "use strict";
    /**
     * Controller for the items shipping tab.
     */
    EloueDashboardApp.controller("ItemsShippingCtrl", [
        "$scope",
        "$stateParams",
        "$timeout",
        "Endpoints",
        "ProductsService",
        "ProductShippingPointsService",
        "ShippingPointsService",
        "UsersService",
        function ($scope, $stateParams, $timeout, Endpoints, ProductsService, ProductShippingPointsService, ShippingPointsService, UsersService) {
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
            $scope.errors = {};

            $scope.handleResponseErrors = function (error, object, action) {
                $scope.submitInProgress = false;
                $scope.showNotification(object, action, false);
            };

            ProductShippingPointsService.getByProduct($stateParams.id).then($scope.applyProductShippingPoints);

            $scope.applyProductShippingPoints = function (data) {
                if (!!data.results && data.results.length > 0) {
                    $scope.productShippingPoint = data.results[0];
                    $scope.fillInSchedule($scope.productShippingPoint.opening_dates);
                    $scope.showPointDetails = true;
                } else {
                    $scope.showWellcome = true;
                }
            };

            if (!$scope.currentUserPromise) {
                $scope.currentUserPromise = UsersService.getMe();
            }
            $scope.currentUserPromise.then(function (currentUser) {
                $scope.currentUser = currentUser;
            });

            $scope.makeInitialSearchByAddress = function () {
                ProductsService.getProduct($stateParams.id, true, false, false, false).then($scope.applyProductDetails);
            };

            $scope.applyProductDetails = function (product) {
                var location = false;
                if ($scope.showPointList && product.address && product.address.street && product.address.city) {
                    $scope.addressQuery = product.address.street + ", " + product.address.city;
                    location = $scope.addressQuery;
                }
                $("#product-shipping-address").formmapper({
                    details: "form",
                    location: location
                });
                $scope.searchShippingPoints();
            };

            $scope.fillInSchedule = function (openingDates) {
                $scope.schedule = {};
                angular.forEach(openingDates, function (value, key) {
                    $scope.schedule[value.day_of_week] = $scope.filterTime(value.morning_opening_time) + " - " +
                        $scope.filterTime(value.morning_closing_time) + ", " +
                        $scope.filterTime(value.afternoon_opening_time) + " - " +
                        $scope.filterTime(value.afternoon_closing_time);
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
                    ProductShippingPointsService.deleteShippingPoint($scope.productShippingPoint.id).then(function () {
                        $scope.savePoint();
                    }, function (error) {
                        $scope.handleResponseErrors(error, "shipping_point", "delete");
                    });
                } else {
                    $scope.savePoint();
                }
            };

            $scope.savePoint = function () {
                var selectedPoint = {};
                angular.forEach($scope.shippingPoints, function (value, key) {
                    if ($scope.selectedPointId === value.site_id) {
                        selectedPoint = value;
                    }
                });
                selectedPoint.product = $scope.productsBaseUrl + $stateParams.id + "/";
                selectedPoint.type = 1;
                ProductShippingPointsService.saveShippingPoint(selectedPoint).then(
                    $scope.parseShippingPointResult,
                    function (error) {
                        $scope.handleResponseErrors(error, "shipping_point", "save");
                    }
                );
            };

            $scope.parseShippingPointResult = function (result) {
                $scope.productShippingPoint = result;
                $scope.submitInProgress = false;
                $scope.showNotification("shipping_point", "save", true);
                $scope.fillInSchedule($scope.productShippingPoint.opening_dates);
                $scope.showMapPointDetails();
            };

            $scope.pointSelected = function (pointId) {
                $scope.selectedPointId = pointId;
            };

            $scope.cancelPointSelection = function () {
                $scope.showWellcomeScreen();
            };

            $scope.removeMapPoint = function () {
                ProductShippingPointsService.deleteShippingPoint($scope.productShippingPoint.id).then(function () {
                    $scope.productShippingPoint = {};
                    $scope.showWellcomeScreen();
                });
            };

            $scope.searchShippingPoints = function () {
                $timeout(function () {
                    var searchLat = $("#searchLat").attr("value"), searchLng = $("#searchLng").attr("value");
                    if (!!searchLat && !!searchLng) {
                        $scope.submitInProgress = true;
                        ShippingPointsService.searchDepartureShippingPointsByCoordinates(searchLat, searchLng).then(function (data) {
                            $scope.shippingPoints = data;
                            $scope.submitInProgress = false;
                        }, function (error) {
                            if (error.detail) {
                                $scope.errors.general = error.detail;
                            } else {
                                $scope.errors.general = "Search point list fault";
                            }
                            $scope.submitInProgress = false;
                        });
                    }
                }, 500);
            };
        }]);
});
