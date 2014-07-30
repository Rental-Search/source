define(["angular", "eloue/app"], function (angular) {
    "use strict";

    /**
     * Controller for dashboard main page.
     */
    angular.module("EloueDashboardApp").controller("DashboardCtrl", ["$scope", function ($scope) {
        $scope.header_text = "Dashboard";
    }]);
});