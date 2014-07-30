define(["angular", "eloue/app"], function (angular) {
    "use strict";

    /**
     * Controller for dashboard main page.
     */
    angular.module("EloueDashboardApp").controller("DashboardCtrl", ["$scope", "$cookieStore", function ($scope, $cookieStore) {
        $scope.header_text = "Dashboard";
    }]);
});