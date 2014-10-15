"use strict";

define(["angular", "toastr", "eloue/app"], function (angular, toastr) {

    /**
     * Controller for the booking detail page.
     */
    angular.module("EloueDashboardApp").controller("BookingDetailCtrl", [
        "$scope",
        "$stateParams",
        "Endpoints",
        "BookingsLoadService",
        "CommentsLoadService",
        "PhoneNumbersService",
        "UsersService",
        "UtilsService",
        function ($scope, $stateParams, Endpoints, BookingsLoadService, CommentsLoadService, PhoneNumbersService, UsersService, UtilsService) {

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
                console.log(bookingDetails);
                $scope.bookingDetails = bookingDetails;
                $scope.bookingDetails.state = "authorized";
                $scope.currentUserPromise.then(function (currentUser) {
                    $scope.currentUserUrl = Endpoints.api_url + "users/" + currentUser.id + "/";
                    $scope.isOwner = bookingDetails.owner.indexOf($scope.currentUserUrl) != -1;
                    $scope.isBorrower = bookingDetails.borrower.indexOf($scope.currentUserUrl) != -1;

                });
                UsersService.get(UtilsService.getIdFromUrl(bookingDetails.borrower)).$promise.then(function(result) {
                    $scope.borrowerName = result.username;
                    $scope.borrowerSlug = result.slug;
                });

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
                // Load comments
                CommentsLoadService.getCommentList($stateParams.uuid).then(function (commentList) {
                    $scope.commentList = commentList;
                    $scope.showCommentForm = !!$scope.commentList && $scope.bookingDetails.state == "ended";
                });
            });

            /**
             * Show real number of the owner if the booking have the pending status and after.
             * @param status booking status
             * @returns show be real number shown
             */
            $scope.showRealPhoneNumber = function(status) {
                return $.inArray(status, ["pending", "ongoing", "ended", "incident", "refunded", "closed"]) != -1;
            };


            $scope.acceptBooking = function() {
                BookingsLoadService.acceptBooking($stateParams.uuid).$promise.then(function(result) {
                    toastr.options.positionClass = "toast-top-full-width";
                    toastr.success(result.detail, "");
                })
            };

            $scope.rejectBooking = function() {
                BookingsLoadService.rejectBooking($stateParams.uuid).$promise.then(function(result) {
                    toastr.options.positionClass = "toast-top-full-width";
                    toastr.success(result.detail, "");
                })
            };

            $scope.cancelBooking = function() {
                console.log($stateParams.uuid);
                BookingsLoadService.cancelBooking($stateParams.uuid).$promise.then(function(result) {
                    toastr.options.positionClass = "toast-top-full-width";
                    toastr.success(result.detail, "");
                })
            };

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