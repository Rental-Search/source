"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the account's invitation page.
     */
    angular.module("EloueDashboardApp").controller("AccountInvitationCtrl", ["$scope", function ($scope) {
        $scope.markListItemAsSelected("account-part-", "account.invitation");
        $scope.title = "Invitation title";
    }]);
});