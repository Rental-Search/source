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
            BookingsService.getBookingDetailInformation($stateParams.uuid).then(function (bookingDetail) {
                $scope.bookingDetail = bookingDetail;

                // Initiate custom scrollbars
                $scope.initCustomScrollbars();
            });
        }
    ]);
});