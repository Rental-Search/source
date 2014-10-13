"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items tariffs tab.
     */
    angular.module("EloueDashboardApp").controller("ItemsTariffsCtrl", [
        "$q",
        "$scope",
        "$stateParams",
        "Endpoints",
        "Currency",
        "Unit",
        "CategoriesService",
        "ProductsService",
        "PricesService",
        function ($q, $scope, $stateParams, Endpoints, Currency, Unit, CategoriesService, ProductsService, PricesService) {

            $scope.units = Unit;
            $scope.prices = {
                hour: {id: null, amount: null, unit: Unit.HOUR.id},
                day: {id: null, amount: null, unit: Unit.DAY.id},
                three_days: {id: null, amount: null, unit: Unit.THREE_DAYS.id},
                seven_days: {id: null, amount: null, unit: Unit.WEEK.id},
                fifteen_days: {id: null, amount: null, unit: Unit.FIFTEEN_DAYS.id}
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
                        case Unit.WEEK.id:
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
                $scope.submitInProgress = true;
                var promises = [];
                angular.forEach($scope.prices, function (value, key) {
                    if (value.amount && value.amount > 0) {
                        value.currency = Currency.EUR.name;
                        value.product = Endpoints.api_url + "products/" + $scope.product.id + "/";
                        if (value.id) {
                            promises.push(PricesService.updatePrice(value).$promise);
                        } else {
                            promises.push(PricesService.savePrice(value).$promise);
                        }
                    }
                });
                var addressId, phoneId;
                if (!!$scope.product.address) {
                    addressId = $scope.product.address.id;
                    if (!!addressId) {
                        $scope.product.address = Endpoints.api_url + "addresses/" + addressId + "/";
                    }
                }
                if (!!$scope.product.phone) {
                    phoneId = $scope.product.phone.id;
                    if (!!phoneId) {
                        $scope.product.phone = Endpoints.api_url + "phones/" + phoneId + "/";
                    }
                }

                promises.push(ProductsService.updateProduct($scope.product).$promise);
                $q.all(promises).then(function(results) {
                    $scope.submitInProgress = false;
                    $scope.product.address = {
                        id: addressId
                    };
                    $scope.product.phone = {
                        id: phoneId
                    };
                });
            }
        }]);
});