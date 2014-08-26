"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items tariffs tab.
     */
    angular.module("EloueDashboardApp").controller("ItemsTariffsCtrl", [
        "$scope",
        "$stateParams",
        "Endpoints",
        "Currency",
        "Unit",
        "CategoriesService",
        "ProductsService",
        "PricesService",
        function ($scope, $stateParams, Endpoints, Currency, Unit, CategoriesService, ProductsService, PricesService) {

            $scope.units = Unit;
            $scope.prices = {
                hour: {id: null, amount: 0, unit: Unit.HOUR.id},
                day: {id: null, amount: 0, unit: Unit.DAY.id},
                three_days: {id: null, amount: 0, unit: Unit.THREE_DAYS.id},
                seven_days: {id: null, amount: 0, unit: Unit.SEVEN_DAYS.id},
                fifteen_days: {id: null, amount: 0, unit: Unit.FIFTEEN_DAYS.id}
            };
            $scope.isAuto = false;
            $scope.isRealEstate = false;

            ProductsService.getProductDetails($stateParams.id).then(function (product) {
                $scope.product = product;
                CategoriesService.getParentCategory($scope.product.categoryDetails).$promise.then(function (nodeCategory) {
                    CategoriesService.getParentCategory(nodeCategory).$promise.then(function (rootCategory) {
                        $scope.updateFieldSet(rootCategory);
                    });
                });
            });

            PricesService.getPricesByProduct($stateParams.id).$promise.then(function (prices) {
                angular.forEach(prices.results, function (value, key) {
                    switch (value.unit) {
                        case Unit.HOUR.id:
                            $scope.prices.hour.amount = value.amount;
                            $scope.prices.hour.id = value.id;
                            break;
                        case Unit.DAY.id:
                            $scope.prices.day.amount = value.amount;
                            $scope.prices.day.id = value.id;
                            break;
                        case Unit.THREE_DAYS.id:
                            $scope.prices.three_days.amount = value.amount;
                            $scope.prices.three_days.id = value.id;
                            break;
                        case Unit.SEVEN_DAYS.id:
                            $scope.prices.seven_days.amount = value.amount;
                            $scope.prices.seven_days.id = value.id;
                            break;
                        case Unit.FIFTEEN_DAYS.id:
                            $scope.prices.fifteen_days.amount = value.amount;
                            $scope.prices.fifteen_days.id = value.id;
                            break;
                    }
                });
            });

            $scope.updateFieldSet = function (rootCategory) {
                $scope.isAuto = false;
                $scope.isRealEstate = false;
                if (rootCategory.name === "Automobile") {
                    $scope.isAuto = true;
                } else if (rootCategory.name === "Hébergement") {
                    $scope.isRealEstate = true;
                }
            };

            $scope.updatePrices = function () {
                angular.forEach($scope.prices, function (value, key) {
                    value.currency = Currency.EUR.name;
                    value.product = Endpoints.api_url + "products/" + $scope.product.id + "/";
                    if (value.id) {
                        PricesService.updatePrice(value);
                    } else {
                        PricesService.savePrice(value);
                    }

                });
                ProductsService.updateProduct($scope.product);
            }
        }]);
});