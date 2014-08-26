"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items terms tab.
     */
    angular.module("EloueDashboardApp").controller("ItemsTermsCtrl", [
        "$scope",
        "$stateParams",
        "CategoriesService",
        "ProductsService",
        function ($scope, $stateParams, CategoriesService, ProductsService) {

            $scope.isProfessional = false;
            $scope.isAuto = false;
            $scope.isRealEstate = false;

            ProductsService.getProductDetails($stateParams.id).then(function (product) {
                $scope.product = product;
                console.log(product.ownerDetails.is_professional);
                $scope.isPrfessional = product.ownerDetails.is_professional;
                CategoriesService.getParentCategory($scope.product.categoryDetails).$promise.then(function (nodeCategory) {
                    CategoriesService.getParentCategory(nodeCategory).$promise.then(function (rootCategory) {
                        $scope.updateTermsBlocks(rootCategory);
                    });
                });
            });

            $scope.updateTermsBlocks = function (rootCategory) {
                $scope.isAuto = false;
                $scope.isRealEstate = false;
                if (rootCategory.name === "Automobile") {
                    $scope.isAuto = true;
                } else if (rootCategory.name === "Hébergement") {
                    $scope.isRealEstate = true;
                }
            }
        }]);
});
