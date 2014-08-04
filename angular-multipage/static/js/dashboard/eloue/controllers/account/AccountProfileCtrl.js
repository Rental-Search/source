"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the account's profile page.
     */
    angular.module("EloueDashboardApp").controller("AccountProfileCtrl", ["$scope", "FileReader", function ($scope, FileReader) {
        $scope.title = "Profile title";
    }]);
});