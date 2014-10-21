"use strict";

define(["angular", "toastr", "eloue/app"], function (angular, toastr) {

    /**
     * Controller for the message detail page.
     */
    angular.module("EloueDashboardApp").controller("NewMessageThreadCtrl", [
        "$scope",
        "$state",
        "$stateParams",
        "$q",
        "Endpoints",
        "MessageThreadsService",
        "MessageThreadsLoadService",
        "BookingsLoadService",
        "ProductRelatedMessagesLoadService",
        "ProductsLoadService",
        "UtilsService",
        function ($scope, $state, $stateParams, $q, Endpoints, MessageThreadsService, MessageThreadsLoadService, BookingsLoadService, ProductRelatedMessagesLoadService, ProductsLoadService, UtilsService) {
            $scope.currentUserPromise.then(function (currentUser) {

                $scope.currentUserUrl = Endpoints.api_url + "users/" + currentUser.id + "/";

                if ($stateParams.productId) {
                    $scope.messageThread = {
                        id: null
                    };

                    //Get product details
                    ProductsLoadService.getProduct($stateParams.productId, true, true, true, true).then(function (product) {
                        $scope.messageThread.product = product;
                    });

                    // Get booking product
                    BookingsLoadService.getBookingByProduct($stateParams.productId).then(function (booking) {
                        $scope.booking = booking;
                        $scope.isBorrower = booking.borrower.indexOf($scope.currentUserUrl) != -1;
                        $scope.contractLink = Endpoints.api_url + "bookings/" + $scope.booking.uuid + "/contract/";
                    });
                } else {
                    toastr.options.positionClass = "toast-top-full-width";
                    toastr.error("No product selected", "");
                }

                // Post new message
                $scope.postNewMessage = function () {
                    $scope.submitInProgress = true;
                    ProductRelatedMessagesLoadService.postMessage($scope.messageThread.id, currentUser.id, UtilsService.getIdFromUrl($scope.booking.owner),
                        $scope.message, null, $stateParams.productId).then(function (result) {
                            // Clear message field
                            $scope.message = "";
                            $scope.submitInProgress = false;
                            $stateParams.id = UtilsService.getIdFromUrl(result.thread);
                            $state.transitionTo("messages.detail", $stateParams, { reload: true });
                        });
                };

                $scope.cancelBooking = function () {
                    BookingsLoadService.cancelBooking($scope.booking.uuid).$promise.then(function (result) {
                        toastr.options.positionClass = "toast-top-full-width";
                        toastr.success(result.detail, "");
                        $stateParams.uuid = $scope.booking.uuid;
                        $state.transitionTo("booking.detail", $stateParams, { reload: true });
                    })
                };

                // Initiate custom scrollbars
                $scope.initCustomScrollbars();
            });
        }
    ]);
});
