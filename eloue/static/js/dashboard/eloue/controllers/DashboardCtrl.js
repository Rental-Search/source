define([
    "eloue/app",
    "../../../common/eloue/values",
    "../../../common/eloue/services/UsersService"
], function (EloueDashboardApp) {
    "use strict";
    /**
     * Controller for the dashboard page.
     */
    EloueDashboardApp.controller("DashboardCtrl", [
        "$scope",
        "ActivityType",
        "UsersService",
        function ($scope, ActivityType, UsersService) {

            $scope.activityTypes = ActivityType;
            $scope.selectedActivityType = "";
            $scope.products = {};
            $scope.bookings = {};

            if (!$scope.currentUserPromise) {
                $scope.currentUserPromise = UsersService.getMe().$promise;
            }
            if (!$scope.currentUserPromise) {
                $scope.currentUserPromise = UsersService.getMe().$promise;
            }
            $scope.currentUserPromise.then(function (currentUser) {
                // Save current user in the scope
                $scope.currentUser = currentUser;
                UsersService.getStatistics($scope.currentUser.id).$promise.then(function (stats) {
                    $scope.userStats = stats;
                });
            });
        }]);
});
