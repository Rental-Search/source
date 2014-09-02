"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the messages page.
     */
    angular.module("EloueDashboardApp").controller("MessagesCtrl", [
        "$scope",
        "MessageThreadsLoadService",
        function ($scope, MessageThreadsLoadService) {
            // Get all message threads
            MessageThreadsLoadService.getMessageThreadList(true, true).then(function (messageThreadList) {
                $scope.messageThreadList = messageThreadList;

                // Initiate custom scrollbars
                $scope.initCustomScrollbars();
            });
        }
    ]);
});