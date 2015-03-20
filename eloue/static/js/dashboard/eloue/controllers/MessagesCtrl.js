define([
    "eloue/app",
    "../../../common/eloue/services/UsersService",
    "../../../common/eloue/services/UtilsService"
], function (EloueDashboardApp) {
    "use strict";
    /**
     * Controller for the messages page.
     */
    EloueDashboardApp.controller("MessagesCtrl", [
        "$scope",
        "UsersService",
        "UtilsService",
        function ($scope, UsersService) {
            $scope.messageThreadList = [];

            $scope.showMessages = false;

            if (!$scope.currentUserPromise) {
                $scope.currentUserPromise = UsersService.getMe();
            }
            $scope.currentUserPromise.then(function (currentUser) {
                $scope.currentUser = currentUser;
                $scope.$broadcast("startLoading", {parameters: [], shouldReloadList: true});
                $scope.updateStatistics();
            });

            // Special case when user tries to send message from reservations while he has no
            // message threads yet. It will display message threads block and field to send message.
            $scope.$on("newMessage", function(event, args) {
                $scope.showMessages = args.showMessages;
            });
        }
    ]);
});
