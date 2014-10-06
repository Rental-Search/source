"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the messages page.
     */
    angular.module("EloueDashboardApp").controller("MessagesCtrl", [
        "$scope",
        "$rootScope",
        function ($scope, $rootScope) {
            $scope.messageThreadList = [];
            $scope.currentUserPromise.then(function (currentUser) {
                $scope.currentUser = currentUser;
                $scope.$broadcast("startLoading", {parameters: [true, true], shouldReloadList: true});
            });
        }
    ]);
});