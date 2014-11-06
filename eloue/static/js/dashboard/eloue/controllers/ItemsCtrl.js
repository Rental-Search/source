"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items page.
     */
    angular.module("EloueDashboardApp").controller("ItemsCtrl", [
        "$scope",
        "$timeout",
        "CategoriesService",
        "UsersService",
        function ($scope, $timeout, CategoriesService, UsersService) {

            $scope.selectedCategory = "";
            $scope.currentUser = {};
            $scope.items = [];
            if (!$scope.currentUserPromise) {
                $scope.currentUserPromise = UsersService.getMe().$promise;
            }
            $scope.currentUserPromise.then(function (currentUser) {
                // Save current user in the scope
                $scope.currentUser = currentUser;
                $scope.$broadcast("startLoading", {parameters: [$scope.currentUser.id, $scope.selectedCategory], shouldReloadList: true});
            });

            CategoriesService.getRootCategories().then(function (categories) {
                $scope.categories = categories;
                $timeout(function () {
                    $("#categoryFilterSelect").chosen();
                    $(".chosen-drop").mCustomScrollbar({
                        scrollInertia: '100',
                        autoHideScrollbar: true,
                        theme: 'dark-thin',
                        scrollbarPosition: 'outside',
                        advanced:{
                            autoScrollOnFocus: false,
                            updateOnContentResize: true
                        }
                    });
                }, 500);
            });

            $scope.filterByCategory = function () {
                $scope.$broadcast("startLoading", {parameters: [$scope.currentUser.id, $scope.selectedCategory], shouldReloadList: true});
            }
        }]);
});