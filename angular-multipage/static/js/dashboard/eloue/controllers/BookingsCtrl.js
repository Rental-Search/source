"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the bookings page.
     */
    angular.module("EloueDashboardApp").controller("BookingsCtrl", [
        "$scope",
        "BookingsService",
        function ($scope, BookingsService) {
            BookingsService.getBookings().then(function (bookings) {
                $scope.bookings = bookings;
            });
        }
    ]);
});