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
        "UsersService",
        function ($scope, $stateParams, $q, MessageThreadsService, ProductRelatedMessagesService, UsersService) {

            var promises = {
                currentUser: UsersService.getMe().$promise,
                data: MessageThreadsService.getMessages($stateParams.id)
            };

            $q.all(promises).then(function (results) {
                // Set messages
                $scope.messages = results.data.messages;

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
                    ProductRelatedMessagesService.postMessage($stateParams.id, $scope.recipientId, $scope.message, null)
                        .then(function () {
                            $scope.message = "";
                            MessageThreadsService.getMessages($stateParams.id).then(function (data) {
                                $scope.messages = data.messages;
                            });
                        });
                };
            });
        }
    ]);
});