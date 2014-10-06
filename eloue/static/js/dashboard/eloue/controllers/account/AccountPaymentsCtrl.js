"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the account's payments page.
     */
    angular.module("EloueDashboardApp").controller("AccountPaymentsCtrl", ["$scope", function ($scope) {
        $scope.markListItemAsSelected("account-part-", "account.payments");
        $scope.title = "Payments title";
    }]);
});