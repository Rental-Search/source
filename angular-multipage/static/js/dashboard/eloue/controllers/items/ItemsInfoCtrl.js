"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items photos and info page.
     */
    angular.module("EloueDashboardApp").controller("ItemsInfoCtrl", [
        "$scope",
        "$stateParams",
        "CategoriesService",
        "PicturesService",
        "ProductsService",
        function ($scope, $stateParams, CategoriesService, PicturesService, ProductsService) {

            $scope.rootCategories = {};
            $scope.nodeCategories = {};
            $scope.leafCategories = {};
            $scope.pictures = {};
            $scope.rootCategory = {};
            $scope.nodeCategory = {};

            ProductsService.getProduct($stateParams.id).$promise.then(function (product) {
                $scope.product = product;

                // Initiate custom scrollbars
                $scope.initCustomScrollbars();

                PicturesService.getPicturesByProduct(product.id).$promise.then(function (pictures) {
                    $scope.pictures = pictures.results;
                });
            });

            CategoriesService.getRootCategories().$promise.then(function (categories) {
                $scope.rootCategories = categories.results;
            });

            $scope.updateProduct = function () {
                //TODO: save updated product
            };

            $scope.updateNodeCategories = function () {
                CategoriesService.getChildCategories($scope.rootCategory).$promise.then(function (categories) {
                    $scope.nodeCategories = categories.results;
                });
            };

            $scope.updateLeafCategories = function () {
                CategoriesService.getChildCategories($scope.nodeCategory).$promise.then(function (categories) {
                    $scope.leafCategories = categories.results;
                });
            }
        }
    ]);
});
