"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the account's verification page.
     */
    angular.module("EloueDashboardApp").controller("AccountVerificationCtrl", ["$scope", function ($scope) {
        $scope.title = "Verification title";
    }]);
});