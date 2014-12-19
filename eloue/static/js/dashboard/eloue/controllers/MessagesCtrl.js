"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the messages page.
     */
    angular.module("EloueDashboardApp").controller("MessagesCtrl", [
        "$scope",
        "UsersService",
        "UtilsService",
        function ($scope, UsersService, UtilsService) {
            $scope.messageThreadList = [];
            if (!$scope.currentUserPromise) {
                $scope.currentUserPromise = UsersService.getMe().$promise;
            }
            $scope.currentUserPromise.then(function (currentUser) {
                $scope.currentUser = currentUser;
                $scope.$broadcast("startLoading", {parameters: [], shouldReloadList: true});
            });

            $scope.shouldMarkAsUnread = function (lastMessage) {
                return !lastMessage.read_at && (UtilsService.getIdFromUrl(lastMessage.recipient) == $scope.currentUser.id);
            };
        }
    ]);
});
