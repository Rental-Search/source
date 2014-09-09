"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items page.
     */
    angular.module("EloueDashboardApp").controller("DashboardLoginCtrl", [
        "$scope", "$timeout",
        function ($scope, $timeout) {
            $timeout(function () {
                $("#loginModal").modal("show");
            }, 300);
        }]);
});
