define(["eloue/app"], function (EloueDashboardApp) {
    "use strict";
    /**
     * Controller for the account's verification page.
     */
    EloueDashboardApp.controller("AccountVerificationCtrl", ["$scope", function ($scope) {
        $scope.markListItemAsSelected("account-part-", "account.verification");
        $scope.title = "Verification title";
    }]);
});
