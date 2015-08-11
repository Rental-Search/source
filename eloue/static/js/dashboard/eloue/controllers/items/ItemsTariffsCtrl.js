define([
    "eloue/app",
    "../../../../common/eloue/values",
    "../../../../common/eloue/services/CategoriesService",
    "../../../../common/eloue/services/ProductsService",
    "../../../../common/eloue/services/PricesService"
], function (EloueDashboardApp) {
    "use strict";
    /**
     * Controller for the items tariffs tab.
     */
    EloueDashboardApp.controller("ItemsTariffsCtrl", [
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

            $scope.handleResponseErrors = function (error, object, action) {
                $scope.submitInProgress = false;
                $scope.showNotification(object, action, false);
            };

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

            ProductsService.getProductDetails($stateParams.id).then(
                function (product) {
                    $scope.applyProductDetails(product);
                }
            );

            $scope.applyProductDetails = function (product) {
                $scope.product = product;
                $scope.markListItemAsSelected("item-tab-", "tariffs");

                angular.forEach(product.prices, function (value, key) {
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

                CategoriesService.getParentCategory($scope.product.category).then(function (nodeCategory) {
                    if (!nodeCategory.parent) {
                        $scope.updateFieldSet(nodeCategory);
                    } else {
                        CategoriesService.getParentCategory(nodeCategory).then(function (rootCategory) {
                            $scope.updateFieldSet(rootCategory);
                        });
                    }
                    $scope.product.category = Endpoints.api_url + "categories/" + $scope.product.category.id + "/";
                });
            };

            $scope.updateFieldSet = function (rootCategory) {
                $scope.isAuto = false;
                $scope.isRealEstate = false;
                if (rootCategory.name === "Automobile") {
                    $scope.isAuto = true;
                } else if (rootCategory.name === "Location saisonnière") {
                    $scope.isRealEstate = true;
                }
            };

            $scope.updatePrices = function () {
                $scope.submitInProgress = true;
                var promises = [], addressId, phoneId;
                angular.forEach($scope.prices, function (value, key) {
                    var promise;
                    if (value.amount && value.amount > 0) {
                        value.currency = Currency.EUR.name;
                        value.product = Endpoints.api_url + "products/" + $scope.product.id + "/";
                        if (value.id) {
                            promise = PricesService.updatePrice(value);
                        } else {
                            promise = PricesService.savePrice(value);
                        }
                        promise.then(function (result) {
                            $scope.prices[key].id = result.id;
                            $scope.prices[key].amount = parseFloat(result.amount).toFixed(2);
                        });
                        promises.push(promise);
                    }
                });
                if ($scope.product.address) {
                    addressId = $scope.product.address.id;
                    if (addressId) {
                        $scope.product.address = Endpoints.api_url + "addresses/" + addressId + "/";
                    }
                }
                if ($scope.product.phone) {
                    phoneId = $scope.product.phone.id;
                    if (phoneId) {
                        $scope.product.phone = Endpoints.api_url + "phones/" + phoneId + "/";
                    } else {
                        $scope.product.phone = null;
                    }
                }

                promises.push(ProductsService.updateProduct($scope.product));
                $q.all(promises).then(function (results) {
                    $("#item-title-price-" + $scope.product.id).text($scope.prices.day.amount + "€ / jour");
                    $scope.submitInProgress = false;
                    $scope.showNotification("item_prices", "save", true);
                    
                    // Get the price by day                        
                    var price_by_day;
                    
                    angular.forEach($scope.product.prices, function (value, key) {
                        if (value.unit == 1) {
                            price_by_day = value.amount;
                        }
                    });

                    analytics.track('Item Prices Updated', {
                        'product id': $scope.product.id,
                        'summary': $scope.product.summary,
                        'price by day': price_by_day
                    });
                    
                }, function (error) {
                    $scope.handleResponseErrors(error, "item_prices", "save");
                });
            };
        }]);
});
