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

            // Initial comment data
            $scope.comment = {rate: 5};

            // On rating star click
            $(".star i").click(function () {
                var self = $(this);
                $scope.$apply(function () {
                    $scope.comment.rate = self.attr("rate");
                });
            });

            // Load booking details
            BookingsLoadService.getBookingDetails($stateParams.uuid).then(function (bookingDetails) {
                $scope.bookingDetails = bookingDetails;
                $scope.markListItemAsSelected("booking-", $stateParams.uuid);

                // Initiate custom scrollbars
                $scope.initCustomScrollbars();
            });

            // Load comments
            CommentsLoadService.getCommentList($stateParams.uuid).then(function (commentList) {
                $scope.commentList = commentList;
            });

            // Method to post new comment
            $scope.postComment = function () {
                CommentsLoadService.postComment($stateParams.uuid, $scope.comment.text, $scope.comment.rate).$promise
                    .then(function () {
                        $scope.comment = {
                            text: "",
                            rate: 5
                        };
                    });
            };

        }
    ]);
});