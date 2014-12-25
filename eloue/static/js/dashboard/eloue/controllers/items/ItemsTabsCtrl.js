define(["eloue/app"], function (EloueDashboardApp) {
    "use strict";
    /**
     * Controller for the tabs on item details pages.
     */
    EloueDashboardApp.controller("ItemsTabsCtrl", ["$scope", "$stateParams", function ($scope, $stateParams) {
        $scope.selectedItemId = $stateParams.id;
    }]);
});
