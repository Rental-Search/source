"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the booking detail page.
     */
    angular.module("EloueDashboardApp").controller("BookingDetailCtrl", [
        "$scope",
        "$stateParams",
        "BookingsLoadService",
        "CommentsLoadService",
        function ($scope, $stateParams, BookingsLoadService, CommentsLoadService) {

            // Load booking details
            BookingsLoadService.getBookingDetails($stateParams.uuid).then(function (bookingDetails) {
                $scope.bookingDetails = bookingDetails;

                // Initiate custom scrollbars
                $scope.initCustomScrollbars();
            });

            // Load comments
            CommentsLoadService.getCommentList($stateParams.uuid).then(function (commentList) {
                $scope.commentList = commentList;
            });

            // Method to post new comment
            $scope.postComment = function () {
                // TODO change rate
                CommentsLoadService.postComment($stateParams.uuid, $scope.comment, 4);
            };

        }
    ]);
});