"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items page.
     */
    angular.module("EloueDashboardApp").controller("ItemsCtrl", [
        "$scope",
        "$timeout",
        "$q",
        "ProductsService",
        "UsersService",
        "CategoriesService",
        function ($scope, $timeout, $q, ProductsService, UsersService, CategoriesService) {

            $scope.selectedCategory = "";
            $scope.distance = 0;
            $scope.paginating = false;
            $scope.enabled = true;

            $scope.data = {};
            $scope.data.list = [];
            $scope.pageSize = "10";
            $scope.page = 1;


            UsersService.getMe(function (currentUser) {
                // Save current user in the scope
                $scope.currentUser = currentUser;

                ProductsService.getProductsByOwnerAndRootCategory($scope.currentUser.id, null, $scope.page).then(function (items) {
                    $scope.items = items;

                    // Initiate custom scrollbars
                    $scope.initCustomScrollbars();
                });
            });

            CategoriesService.getRootCategories().$promise.then(function (categories) {
                $scope.categories = categories.results;
            });

            $scope.filterByCategory = function () {
                ProductsService.getProductsByOwnerAndRootCategory($scope.currentUser.id, $scope.selectedCategory, $scope.page).then(function (items) {
                    $scope.items = items;
                });
            }
        }]);
});