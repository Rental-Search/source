define(["eloue/app"], function (EloueDashboardApp) {
    "use strict";
    /**
     * Controller for the account's phones page.
     */
    EloueDashboardApp.controller("AccountPhonesCtrl", ["$scope", function ($scope) {
        $scope.title = "Phones title";
        $scope.markListItemAsSelected("account-part-", "account.phones");
    }]);
});
