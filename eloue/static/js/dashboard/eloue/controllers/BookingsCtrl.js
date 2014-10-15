"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the bookings page.
     */
    angular.module("EloueDashboardApp").controller("BookingsCtrl", [
        "$q",
        "$scope",
        "$rootScope",
        "Endpoints",
        "BookingsLoadService",
        function ($q, $scope, $rootScope, Endpoints, BookingsLoadService) {

            $scope.currentUserUrl = "";
            $scope.bookingFilter = {};
            $scope.stateList = ["authorized", "rejected", "outdated", "canceled", "pending", "ongoing", "ended", "incident", "refunded", "closed"];
            $scope.bookingList = [];
            $scope.stateFilter = undefined;

            $scope.currentUserPromise.then(function (currentUser) {
                $scope.currentUserUrl = Endpoints.api_url + "users/" + currentUser.id + "/";

                $scope.$broadcast("startLoading", {parameters: [$scope.currentUser.id], shouldReloadList: true});
            });

            $scope.filterByOwner = function () {
                $scope.markListItemAsSelected("filter-", "Propriétaires");
                $scope.bookingFilter.owner = $scope.currentUserUrl;
                $scope.bookingFilter.borrower = undefined;
            };

            $scope.filterByBorrower = function () {
                $scope.markListItemAsSelected("filter-", "Emprunteurs");
                $scope.bookingFilter.owner = undefined;
                $scope.bookingFilter.borrower = $scope.currentUserUrl;
            };

            $scope.filterByBoth = function () {
                $scope.markListItemAsSelected("filter-", "Tous");
                $scope.bookingFilter.owner = undefined;
                $scope.bookingFilter.borrower = undefined;
            };

            $scope.filterByState = function () {
                $scope.bookingFilter.state = $scope.stateFilter;
            };

            $scope.filterByBoth();
            $('.chosen-drop').mCustomScrollbar({
                scrollInertia: '100',
                autoHideScrollbar: true,
                theme: 'dark-thin',
                scrollbarPosition: 'outside',
                advanced:{
                    autoScrollOnFocus: false,
                    updateOnContentResize: true
                }
            });
        }
    ]);
});