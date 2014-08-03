"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the account's addresses  page.
     */
    angular.module("EloueDashboardApp").controller("AccountAddressesCtrl", ["$scope", function ($scope) {
        $scope.title = "Addresses title";
    }]);
});