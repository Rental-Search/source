"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the booking detail page.
     */
    angular.module("EloueDashboardApp").controller("BookingDetailCtrl", [
        "$scope",
        "$stateParams",
        "BookingsLoadService",
        "CommentsService",
        function ($scope, $stateParams, BookingsLoadService, CommentsService) {
            BookingsLoadService.getBookingDetails($stateParams.uuid).then(function (bookingDetails) {
                $scope.bookingDetails = bookingDetails;

                $scope.postComment = function () {
                    // TODO change rate
                    CommentsService.postComment($stateParams.uuid, $scope.comment, 4);
                };

                // Initiate custom scrollbars
                $scope.initCustomScrollbars();
            });
        }
    ]);
});