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
                $scope.markListItemAsSelected("item-tab-", "terms");
                $scope.isProfessional = product.owner.is_professional;
                $scope.initCustomScrollbars();
                CategoriesService.getParentCategory($scope.product.category).$promise.then(function (nodeCategory) {
                    if (!nodeCategory.parent) {
                        $scope.updateTermsBlocks(nodeCategory);
                    } else {
                        CategoriesService.getParentCategory(nodeCategory).$promise.then(function (rootCategory) {
                            $scope.updateTermsBlocks(rootCategory);
                        });
                    }
                });
            });

            $scope.updateTermsBlocks = function (rootCategory) {
                $scope.isAuto = false;
                $scope.isRealEstate = false;
                if (rootCategory.name === "Automobile") {
                    $scope.isAuto = true;
                } else if (rootCategory.name === "Location saisonnière") {
                    $scope.isRealEstate = true;
                }
            }
        }]);
});
