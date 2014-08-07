"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the message detail page.
     */
    angular.module("EloueDashboardApp").controller("MessageDetailCtrl", [
        "$scope",
        "$stateParams",
        function ($scope, $stateParams) {
            $scope.title = "Message detail title: " + $stateParams.id;
        }
    ]);
});