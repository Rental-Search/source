define([
    "eloue/app",
    "toastr",
    "../../../../common/eloue/values",
    "../../../../common/eloue/services/BookingsService",
    "../../../../common/eloue/services/ProductRelatedMessagesService",
    "../../../../common/eloue/services/ProductsService",
    "../../../../common/eloue/services/UtilsService",
    "../../../../common/eloue/services/UsersService"
], function (EloueDashboardApp, toastr) {
    "use strict";
    /**
     * Controller for the page to create new message thread for previously selected booking.
     */
    EloueDashboardApp.controller("NewMessageThreadCtrl", [
        "$scope",
        "$rootScope",
        "$state",
        "$stateParams",
        "Endpoints",
        "BookingsService",
        "ProductRelatedMessagesService",
        "ProductsService",
        "UtilsService",
        "UsersService",
        function ($scope, $rootScope, $state, $stateParams, Endpoints, BookingsService, ProductRelatedMessagesService, ProductsService, UtilsService, UsersService) {

            if (!$scope.currentUserPromise) {
                $scope.currentUserPromise = UsersService.getMe();
            }

            // Broadcast value to display message thread.
            $rootScope.$broadcast("newMessage", {showMessages: true});

            $scope.currentUserPromise.then(function (currentUser) {

                $scope.currentUser = currentUser;
                $scope.currentUserUrl = Endpoints.api_url + "users/" + currentUser.id + "/";

                if ($stateParams.bookingId) {
                    $scope.messageThread = {
                        id: null
                    };

                    // Get booking
                    BookingsService.getBooking($stateParams.bookingId).then(function(booking) {
                        $scope.booking = booking;
                        $scope.messageThread.product = booking.product;
                        $scope.allowDownloadContract = $.inArray($scope.booking.state, ["pending", "ongoing", "ended", "incident", "closed"]) !== -1;
                        $scope.contractLink = Endpoints.api_url + "bookings/" + $scope.booking.uuid + "/contract/";
                    });
                } else {
                    toastr.options.positionClass = "toast-top-full-width";
                    toastr.error("No product selected", "");
                }

                // Initiate custom scrollbars
                $scope.initCustomScrollbars();
                $("#messages-list").find(".load-more-button").hide();
            });

            // Post new message
            $scope.postNewMessage = function () {
                $scope.submitInProgress = true;
                var recipientId = $scope.booking.owner.id == $scope.currentUser.id ? $scope.booking.borrower.id : $scope.booking.owner.id;
                ProductRelatedMessagesService.postMessage($scope.messageThread.id, $scope.currentUser.id, recipientId,
                    $scope.message, null, $scope.booking.product.id).then(
                    $scope.redirectAfterMessagePost,
                    function () {
                        $scope.submitInProgress = false;
                        $scope.showNotification("message", "send", false);
                    }
                );
            };

            $scope.redirectAfterMessagePost = function (result) {
                // Clear message field
                $scope.message = "";
                $scope.submitInProgress = false;
                $scope.showNotification("message", "send", true);
                $stateParams.id = UtilsService.getIdFromUrl(result.thread);
                $state.transitionTo("messages.detail", $stateParams, {reload: true});
            };
        }
    ]);
});
