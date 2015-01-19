define(["eloue/app"], function (EloueDashboardApp) {
    "use strict";
    /**
     * Controller for the account's payments page.
     */
    EloueDashboardApp.controller("AccountPaymentsCtrl", ["$scope", function ($scope) {
        $scope.markListItemAsSelected("account-part-", "account.payments");
        $scope.title = "Payments title";
    }]);
});
