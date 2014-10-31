"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the messages page.
     */
    angular.module("EloueDashboardApp").controller("MessagesCtrl", [
        "$scope",
        "$rootScope",
        "UsersService",
        function ($scope, $rootScope, UsersService) {
            $scope.messageThreadList = [];
            if (!$scope.currentUserPromise) {
                $scope.currentUserPromise = UsersService.getMe().$promise;
            }
            $scope.currentUserPromise.then(function (currentUser) {
                $scope.currentUser = currentUser;
                $scope.$broadcast("startLoading", {parameters: [true, true], shouldReloadList: true});
            });
        }
    ]);
});