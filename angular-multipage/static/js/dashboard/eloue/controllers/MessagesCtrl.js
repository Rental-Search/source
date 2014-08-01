"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the messages page.
     */
    angular.module("EloueDashboardApp").controller("MessagesCtrl", ["$scope", function ($scope) {
        $scope.title = "Messages title";
    }]);
});