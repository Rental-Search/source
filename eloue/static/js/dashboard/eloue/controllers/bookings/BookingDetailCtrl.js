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
        "PhoneNumbersService",
        function ($scope, $stateParams, BookingsLoadService, CommentsLoadService, PhoneNumbersService) {

            // Initial comment data
            $scope.comment = {rate: 0};


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

                if ($scope.bookingDetails.product.phone) {
                    if ($scope.showRealPhoneNumber($scope.bookingDetails.state)) {
                        $scope.phoneNumber = !!$scope.bookingDetails.product.phone.number.numero ? $scope.bookingDetails.product.phone.number.numero : $scope.bookingDetails.product.phone.number;
                    } else {
                        PhoneNumbersService.getPremiumRateNumber($scope.bookingDetails.product.phone.id).$promise.then(function (result) {
                            if (!result.error || result.error == "0") {
                                $scope.phoneNumber = result.numero;
                            }
                        });
                    }
                }

                $scope.markListItemAsSelected("booking-", $stateParams.uuid);
                // Initiate custom scrollbars
                $scope.initCustomScrollbars();
            });

            /**
             * Show real number of the owner if the booking have the pending status and after.
             * @param status booking status
             * @returns show be real number shown
             */
            $scope.showRealPhoneNumber = function(status) {
                return $.inArray(status, ["pending", "ongoing", "ended", "incident", "refunded", "closed"]) != -1;
            };

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