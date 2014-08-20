"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the message detail page.
     */
    angular.module("EloueDashboardApp").controller("MessageDetailCtrl", [
        "$scope",
        "$stateParams",
        "$q",
        "MessageThreadsService",
        "ProductRelatedMessagesService",
        function ($scope, $stateParams, $q, MessageThreadsService, ProductRelatedMessagesService) {

            var promises = {
                currentUser: $scope.currentUserPromise,
                data: MessageThreadsService.getThread($stateParams.id)
            };

            $q.all(promises).then(function (results) {
                // Set messages
                $scope.messages = results.data.messages;

                // Set product
                $scope.product = results.data.product;

                // Find recipient id
                $scope.recipientId = null;
                var stopped = false;
                angular.forEach(results.data.users, function (value) {
                    if ((!stopped) && (value != results.currentUser.id)) {
                        $scope.recipientId = value;
                        stopped = true;
                    }
                });

                $scope.postNewMessage = function () {
                    // TODO change offer param
                    if (!!$scope.recipientId) {
                        ProductRelatedMessagesService.postMessage($stateParams.id, $scope.recipientId, $scope.message, null)
                            .then(function () {
                                $scope.message = "";
                                MessageThreadsService.getMessages($stateParams.id).then(function (data) {
                                    $scope.messages = data.messages;
                                });
                            });
                    }
                };

                // Initiate custom scrollbars
                $scope.initCustomScrollbars();
            });
        }
    ]);
});