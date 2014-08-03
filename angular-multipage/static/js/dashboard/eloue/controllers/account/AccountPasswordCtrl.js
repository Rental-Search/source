"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the account's change password page.
     */
    angular.module("EloueDashboardApp").controller("AccountPasswordCtrl", ["$scope", function ($scope) {
        $scope.title = "Password title";
    }]);
});