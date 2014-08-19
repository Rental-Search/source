"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the booking detail page.
     */
    angular.module("EloueDashboardApp").controller("BookingDetailCtrl", [
        "$scope",
        "$stateParams",
        "BookingsService",
        "CommentsService",
        function ($scope, $stateParams, BookingsService, CommentsService) {
            BookingsService.getBookingDetailInformation($stateParams.uuid).then(function (bookingDetail) {
                $scope.bookingDetail = bookingDetail;

                $scope.postComment = function () {
                    CommentsService.postComment($stateParams.uuid, $scope.comment, 4);
                };

                // Initiate custom scrollbars
                $scope.initCustomScrollbars();
            });
        }
    ]);
});