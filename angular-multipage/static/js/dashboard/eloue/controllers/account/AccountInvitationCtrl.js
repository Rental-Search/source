"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the account's invitation page.
     */
    angular.module("EloueDashboardApp").controller("AccountInvitationCtrl", ["$scope", function ($scope) {
        $scope.title = "Invitation title";
    }]);
});