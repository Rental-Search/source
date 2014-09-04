"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items page.
     */
    angular.module("EloueDashboardApp").controller("DashboardLoginCtrl", [
        "$scope",
        function ($scope) {
            $("#loginModal").modal("show");
        }]);
});
