"use strict";

define(["angular", "eloue/app", "../../../common/eloue/services"], function (angular) {

    /**
     * Controller for the messages page.
     */
    angular.module("EloueDashboardApp").controller("MessagesCtrl", [
        "$scope",
        "MessageThreadsService",
        function ($scope, MessageThreadsService) {
            $scope.title = "Messages title";

            // Get all message threads
            MessageThreadsService.getMessageThreads(function (data) {
                $scope.message_threads = data.results;
            });
        }
    ]);
});