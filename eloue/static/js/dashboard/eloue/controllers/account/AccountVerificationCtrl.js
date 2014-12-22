"use strict";

define(["eloue/app"], function (EloueDashboardApp) {

    /**
     * Controller for the account's verification page.
     */
    EloueDashboardApp.controller("AccountVerificationCtrl", ["$scope", function ($scope) {
        $scope.markListItemAsSelected("account-part-", "account.verification");
        $scope.title = "Verification title";
    }]);
});
