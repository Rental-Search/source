"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the bookings page.
     */
    angular.module("EloueDashboardApp").controller("BookingsCtrl", [
        "$scope",
        "BookingsLoadService",
        function ($scope, BookingsLoadService) {
            BookingsLoadService.getBookingList().then(function (bookingList) {
                $scope.bookingList = bookingList;

                // Initiate custom scrollbars
                $scope.initCustomScrollbars();
            });
        }
    ]);
});