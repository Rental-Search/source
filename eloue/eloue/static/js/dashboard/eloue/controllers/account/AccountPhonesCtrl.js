"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the account's phones page.
     */
    angular.module("EloueDashboardApp").controller("AccountPhonesCtrl", ["$scope", function ($scope) {
        $scope.title = "Phones title";
    }]);
});