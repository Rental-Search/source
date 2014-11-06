"use strict";

define(["angular", "toastr", "eloue/app"], function (angular, toastr) {

    /**
     * Controller for the message detail page.
     */
    angular.module("EloueDashboardApp").controller("NewMessageThreadCtrl", [
        "$scope",
        "$state",
        "$stateParams",
        "Endpoints",
        "BookingsLoadService",
        "ProductRelatedMessagesLoadService",
        "ProductsLoadService",
        "UtilsService",
        "UsersService",
        function ($scope, $state, $stateParams, Endpoints, BookingsLoadService, ProductRelatedMessagesLoadService, ProductsLoadService, UtilsService, UsersService) {

            if (!$scope.currentUserPromise) {
                $scope.currentUserPromise = UsersService.getMe().$promise;
            }
            $scope.currentUserPromise.then(function (currentUser) {

                $scope.currentUserUrl = Endpoints.api_url + "users/" + currentUser.id + "/";

                if ($stateParams.productId) {
                    $scope.messageThread = {
                        id: null
                    };

                    //Get product details
                    ProductsLoadService.getProduct($stateParams.productId, true, true).then(function (product) {
                        $scope.messageThread.product = product;
                    });

                    // Get booking product
                    BookingsLoadService.getBookingByProduct($stateParams.productId).then(function (booking) {
                        $scope.booking = booking;
                        $scope.allowDownloadContract = $.inArray($scope.booking.state, ["pending", "ongoing", "ended", "incident", "closed"]) != -1;
                        $scope.contractLink = Endpoints.api_url + "bookings/" + $scope.booking.uuid + "/contract/";
                    });
                } else {
                    toastr.options.positionClass = "toast-top-full-width";
                    toastr.error("No product selected", "");
                }

                // Post new message
                $scope.postNewMessage = function () {
                    $scope.submitInProgress = true;
                    ProductRelatedMessagesLoadService.postMessage($scope.messageThread.id, currentUser.id, $scope.booking.owner.id,
                        $scope.message, null, $stateParams.productId).then(function (result) {
                            // Clear message field
                            $scope.message = "";
                            $scope.submitInProgress = false;
                            $stateParams.id = UtilsService.getIdFromUrl(result.thread);
                            $state.transitionTo("messages.detail", $stateParams, { reload: true });
                        });
                };

                // Initiate custom scrollbars
                $scope.initCustomScrollbars();
            });
        }
    ]);
});
