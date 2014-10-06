"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items page.
     */
    angular.module("EloueDashboardApp").controller("ItemsCtrl", [
        "$scope",
        "$rootScope",
        "CategoriesService",
        function ($scope, $rootScope, CategoriesService) {

            $scope.selectedCategory = "";
            $scope.currentUser = {};
            $scope.items = [];
            $scope.currentUserPromise.then(function (currentUser) {
                // Save current user in the scope
                $scope.currentUser = currentUser;
                $scope.$broadcast("startLoading", {parameters: [$scope.currentUser.id, $scope.selectedCategory], shouldReloadList: true});
            });

            CategoriesService.getRootCategories().then(function (categories) {
                $scope.categories = categories;
            });

            $scope.filterByCategory = function () {
                $scope.$broadcast("startLoading", {parameters: [$scope.currentUser.id, $scope.selectedCategory], shouldReloadList: true});
            }
        }]);
});