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

                //TODO: change hardcoded "1190" to  $scope.currentUser.id
                ProductsService.getProductsByOwnerAndRootCategory(1190).then(function (items) {
                    $scope.items = items;

                    // Initiate custom scrollbars
                    $scope.initCustomScrollbars();
                });
            });

            CategoriesService.getRootCategories().$promise.then(function (categories) {
                $scope.categories = categories.results;
            });

            $scope.filterByCategory = function () {
                //TODO: change hardcoded "1190" to  $scope.currentUser.id
                ProductsService.getProductsByOwnerAndRootCategory(1190, $scope.selectedCategory).then(function (items) {
                    $scope.items = items;
                });
            }
        }]);
});