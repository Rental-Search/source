"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the message detail page.
     */
    angular.module("EloueDashboardApp").controller("MessageDetailCtrl", [
        "$scope",
        "$stateParams",
        "$q",
        "MessageThreadsLoadService",
        "BookingsLoadService",
        "ProductRelatedMessagesLoadService",
        function ($scope, $stateParams, $q, MessageThreadsLoadService, BookingsLoadService, ProductRelatedMessagesLoadService) {

            var promises = {
                currentUser: $scope.currentUserPromise,
                messageThread: MessageThreadsLoadService.getMessageThread($stateParams.id)
            };

            $q.all(promises).then(function (results) {
                $scope.messageThread = results.messageThread;

                // Get booking product
                BookingsLoadService.getBookingByProduct($scope.messageThread.product.id).then(function (booking) {
                    $scope.booking = booking;
                });

                // Get users' roles
                var usersRoles = MessageThreadsLoadService.getUsersRoles($scope.messageThread, results.currentUser.id);

                // Post new message
                $scope.postNewMessage = function () {
                    ProductRelatedMessagesLoadService.postMessage($stateParams.id, usersRoles.senderId, usersRoles.recipientId,
                        $scope.message, null).then(function () {
                            // Clear message field
                            $scope.message = "";

                            // Reload data
                            MessageThreadsLoadService.getMessageThread($stateParams.id).then(function (messageThread) {
                                $scope.messageThread.messages = messageThread.messages;
                            });
                        });
                };

                // Initiate custom scrollbars
                $scope.initCustomScrollbars();
            });
        }
    ]);
});