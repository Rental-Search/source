"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items profits tab.
     */
    angular.module("EloueDashboardApp").controller("ItemsProfitsCtrl", [
        "$scope",
        "$stateParams",
        "BookingsService",
        function ($scope, $stateParams, BookingsService) {
            $scope.bookings = [];
            $scope.totalProfit = 0;
            $scope.numberOfBookings = 0;
            $scope.durationDays = 0;
            $scope.durationMonths = 0;
            $scope.durationYears = 0;

            BookingsService.getBookingsByProduct($stateParams.id).then(function (bookings) {
                $scope.bookings = bookings;

                angular.forEach($scope.bookings, function (value, key) {

                });
            });
        }]);
});
