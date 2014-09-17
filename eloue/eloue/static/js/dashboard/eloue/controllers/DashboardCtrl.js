"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the dashboard page.
     */
    angular.module("EloueDashboardApp").controller("DashboardCtrl", [
        "$scope",
        "ActivityType",
        "BookingsLoadService",
        "ProductsService",
        "UsersService",
        function ($scope, ActivityType, BookingsLoadService, ProductsService, UsersService) {

            $scope.activityTypes = ActivityType;
            $scope.selectedActivityType = "";
            $scope.products = {};
            $scope.bookings = {};

            $scope.currentUserPromise.then(function (currentUser) {
                // Save current user in the scope
                $scope.currentUser = currentUser;
                UsersService.getStatistics($scope.currentUser.id).$promise.then(function (stats) {
                    $scope.userStats = stats;
                });
                ProductsService.getProductsByOwnerAndRootCategory(currentUser.id).then(function (items) {
                    $scope.products = items.list;
                });
                BookingsLoadService.getBookingList(currentUser.id).then(function (bookingList) {
                    $scope.bookings = bookingList.list;
                });
            });

            $scope.filterByActivityType = function () {
                console.log($scope.selectedActivityType);
                //TODO: filter activity feed
            }
        }]);
});