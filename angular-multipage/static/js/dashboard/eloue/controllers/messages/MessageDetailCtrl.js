"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the message detail page.
     */
    angular.module("EloueDashboardApp").controller("MessageDetailCtrl", [
        "$scope",
        "$stateParams",
        "MessageThreadsService",
        function ($scope, $stateParams, MessageThreadsService) {
            MessageThreadsService.getMessages($stateParams.id).then(function (data) {
                $scope.messages = data;
            });
        }
    ]);
});