"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the account's verification page.
     */
    angular.module("EloueDashboardApp").controller("AccountVerificationCtrl", ["$scope", function ($scope) {
        $scope.markListItemAsSelected("account-part-", "account.verification");
        $scope.title = "Verification title";
    }]);
});