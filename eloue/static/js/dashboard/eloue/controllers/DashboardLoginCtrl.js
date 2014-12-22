"use strict";

define(["eloue/app"], function (EloueDashboardApp) {

    /**
     * Controller for the items page.
     */
    EloueDashboardApp.controller("DashboardLoginCtrl", [
        "$scope", "$timeout",
        function ($scope, $timeout) {
            $timeout(function () {
                $("#loginModal").modal("show");
            }, 300);
        }]);
});
