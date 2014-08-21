"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items tariffs tab.
     */
    angular.module("EloueDashboardApp").controller("ItemsTariffsCtrl", [
        "$scope",
        "$stateParams",
        "Unit",
        "CategoriesService",
        "ProductsService",
        "PricesService",
        function ($scope, $stateParams, Unit, CategoriesService, ProductsService, PricesService) {

            $scope.units = Unit;
            $scope.prices = {};
            $scope.isAuto = false;
            $scope.isRealEstate = false;

            ProductsService.getProductDetails($stateParams.id).then(function (product) {
                $scope.product = product;
                $scope.product.category = $scope.product.categoryDetails.id;
                CategoriesService.getParentCategory($scope.product.categoryDetails).$promise.then(function (nodeCategory) {
                    CategoriesService.getParentCategory(nodeCategory).$promise.then(function (rootCategory) {
                        $scope.rootCategory = rootCategory.id;
                        $scope.updateFieldSet(rootCategory);
                    });
                });
            });

            PricesService.getPricesByProduct($stateParams.id).$promise.then(function (prices) {
                $scope.prices = prices.results;
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
                console.log("updatePrices");
                angular.forEach($scope.prices, function (value, key) {

                });

            }
        }]);
});