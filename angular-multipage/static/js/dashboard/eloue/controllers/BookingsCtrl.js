"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the bookings page.
     */
    angular.module("EloueDashboardApp").controller("BookingsCtrl", ["$scope", function ($scope) {
        $scope.title = "Bookings title";
    }]);
});