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
                    if (!booking) {
                        // Options for the select element
                        $scope.availableHours = [
                            {"label": "00.00", "value": "00:00:00"},
                            {"label": "01.00", "value": "01:00:00"},
                            {"label": "02.00", "value": "02:00:00"},
                            {"label": "03.00", "value": "03:00:00"},
                            {"label": "04.00", "value": "04:00:00"},
                            {"label": "05.00", "value": "05:00:00"},
                            {"label": "06.00", "value": "06:00:00"},
                            {"label": "07.00", "value": "07:00:00"},
                            {"label": "08.00", "value": "08:00:00"},
                            {"label": "09.00", "value": "09:00:00"},
                            {"label": "10.00", "value": "10:00:00"},
                            {"label": "11.00", "value": "11:00:00"},
                            {"label": "12.00", "value": "12:00:00"},
                            {"label": "13.00", "value": "13:00:00"},
                            {"label": "14.00", "value": "14:00:00"},
                            {"label": "15.00", "value": "15:00:00"},
                            {"label": "16.00", "value": "16:00:00"},
                            {"label": "17.00", "value": "17:00:00"},
                            {"label": "18.00", "value": "18:00:00"},
                            {"label": "19.00", "value": "19:00:00"},
                            {"label": "20.00", "value": "20:00:00"},
                            {"label": "21.00", "value": "21:00:00"},
                            {"label": "22.00", "value": "22:00:00"},
                            {"label": "23.00", "value": "23:00:00"}
                        ];

                        $scope.newBooking = {
                            start_time: $scope.availableHours[0],
                            end_time: $scope.availableHours[0]
                        };

                        $scope.calculateBookingPrise = function () {
                            console.log("calculateBookingPrise()");
                        };
                    }
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