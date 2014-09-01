"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items page.
     */
    angular.module("EloueDashboardApp").controller("ItemsCtrl", [
        "$scope",
        "ProductsService",
        "UsersService",
        "CategoriesService",
        function ($scope, ProductsService, UsersService, CategoriesService) {

            $scope.selectedCategory = "";

            UsersService.getMe(function (currentUser) {
                // Save current user in the scope
                $scope.currentUser = currentUser;

                ProductsService.getProductsByOwnerAndRootCategory($scope.currentUser.id).then(function (items) {
                    $scope.items = items;

                    // Initiate custom scrollbars
                    $scope.initCustomScrollbars();
                });
            });

            CategoriesService.getRootCategories().$promise.then(function (categories) {
                $scope.categories = categories.results;
            });

            $scope.filterByCategory = function () {
                ProductsService.getProductsByOwnerAndRootCategory($scope.currentUser.id, $scope.selectedCategory).then(function (items) {
                    $scope.items = items;
                });
            }
        }]);
});