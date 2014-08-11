"use strict";

define(["angular", "eloue/app", "../../../common/eloue/services"], function (angular) {

    /**
     * Controller for the messages page.
     */
    angular.module("EloueDashboardApp").controller("MessagesCtrl", [
        "$scope",
        "MessageThreadsService",
        function ($scope, MessageThreadsService) {
            // Get all message threads
            MessageThreadsService.getMessageThreads().then(function (data) {
                $scope.message_threads = data;
            });
        }
    ]);
});