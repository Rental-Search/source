"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the bookings page.
     */
    angular.module("EloueDashboardApp").controller("BookingsCtrl", [
        "$scope",
        "BookingsService",
        function ($scope, BookingsService) {
            $scope.title = "Bookings title";

            BookingsService.getBookings().then(function (results) {
                console.log("results:");
                console.log(results);
            });
        }
    ]);
});