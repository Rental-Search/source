define(["eloue/app"], function (EloueDashboardApp) {
    "use strict";
    /**
     * Controller for the items page.
     */
    EloueDashboardApp.controller("DashboardLoginCtrl", [
        "$timeout",
        function ($timeout) {
            $timeout(function () {
                $("#loginModal").modal("show");
            }, 300);
        }]);
});
