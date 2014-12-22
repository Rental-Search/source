"use strict";

define(["eloue/app"], function (EloueDashboardApp) {

    /**
     * Controller for the account's phones page.
     */
    EloueDashboardApp.controller("AccountPhonesCtrl", ["$scope", function ($scope) {
        $scope.title = "Phones title";
        $scope.markListItemAsSelected("account-part-", "account.phones");
    }]);
});
