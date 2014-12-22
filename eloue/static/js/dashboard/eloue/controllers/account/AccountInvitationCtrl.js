"use strict";

define(["eloue/app"], function (EloueDashboardApp) {

    /**
     * Controller for the account's invitation page.
     */
    EloueDashboardApp.controller("AccountInvitationCtrl", ["$scope", function ($scope) {
        $scope.markListItemAsSelected("account-part-", "account.invitation");
        $scope.title = "Invitation title";
    }]);
});
