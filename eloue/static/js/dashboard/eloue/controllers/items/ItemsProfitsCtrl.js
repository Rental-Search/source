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
                $scope.markListItemAsSelected("item-tab-", "profits");
                $scope.initCustomScrollbars();

                var sum = 0;
                var startOfBookingPeriod = Date.today();
                var endOfBookingPeriod = Date.today();
                var bookingList = [];
                angular.forEach(bookings, function (value, key) {
                    if (value.state == "closed" || value.state == "ended" || value.state == "incident") {
                        var bookingStartDay = Date.parse(value.start_date.day + " " + value.start_date.month + " " + value.start_date.year);
                        if (bookingStartDay < startOfBookingPeriod) {
                            startOfBookingPeriod = bookingStartDay;
                        }

                        //TODO: maybe should be fixed to sum of transferred amounts
                        sum += parseInt(value.total_amount);
                        bookingList.push(value);
                    }
                });

                $scope.bookings = bookingList;
                $scope.numberOfBookings = bookingList.length;

                //Get duration as difference between actual duration in milliseconds represented as new date and calendar start date - 1.01.1970
                var durationAsDate = new Date(endOfBookingPeriod.getTime() - startOfBookingPeriod.getTime()).add(-1970).years();
                $scope.durationYears = durationAsDate.getFullYear();
                $scope.durationMonths = durationAsDate.getMonth() + 1;
                $scope.durationDays = durationAsDate.getDate();

                $scope.totalProfit = sum;
            });
        }]);
});
