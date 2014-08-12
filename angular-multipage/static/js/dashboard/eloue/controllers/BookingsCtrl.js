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

            BookingsService.getBookings().$promise.then(function (bookings) {
                // TODO change the behavior
                console.log("bookings");
                console.log(bookings);
            });
        }
    ]);
});