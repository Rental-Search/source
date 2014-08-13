"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the booking detail page.
     */
    angular.module("EloueDashboardApp").controller("BookingDetailCtrl", [
        "$scope",
        "$stateParams",
        "BookingsService",
        function ($scope, $stateParams, BookingsService) {
            BookingsService.getBookingDetail($stateParams.uuid).then(function (booking) {
                $scope.booking = booking;
                console.log(booking);
            });
        }
    ]);
});