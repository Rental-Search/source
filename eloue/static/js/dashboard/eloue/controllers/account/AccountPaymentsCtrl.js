"use strict";

define(["eloue/app"], function (EloueDashboardApp) {

    /**
     * Controller for the account's payments page.
     */
    EloueDashboardApp.controller("AccountPaymentsCtrl", ["$scope", function ($scope) {
        $scope.markListItemAsSelected("account-part-", "account.payments");
        $scope.title = "Payments title";
    }]);
});
