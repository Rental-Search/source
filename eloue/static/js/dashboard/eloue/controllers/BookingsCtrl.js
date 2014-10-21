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
            $scope.bookingFilter = {};
            $scope.stateList = ["authorized", "rejected", "outdated", "canceled", "pending", "ongoing", "ended", "incident", "refunded", "closed"];
            $scope.bookingList = [];
            $scope.stateFilter = undefined;

            /**
             * Shows that booking list was not empty and now is being filtered, not to hide left panel with filters when filtered booking list is empty.
             */
            $scope.filtered = false;

            $scope.filterByBoth = function () {
                $scope.markListItemAsSelected("filter-", "Tous");
                $scope.bookingFilter.owner = undefined;
                $scope.bookingFilter.borrower = undefined;
                $scope.filter();
            };

            $scope.currentUserPromise.then(function (currentUser) {
                $scope.currentUser = currentUser;
                $scope.filterByBoth();
            });

            $scope.filterByOwner = function () {
                $scope.filtered = true;
                $scope.markListItemAsSelected("filter-", "Propriétaires");
                $scope.bookingFilter.owner = $scope.currentUser.id;
                $scope.bookingFilter.borrower = undefined;
                $scope.filter();
            };

            $scope.filterByBorrower = function () {
                $scope.filtered = true;
                $scope.markListItemAsSelected("filter-", "Emprunteurs");
                $scope.bookingFilter.owner = undefined;
                $scope.bookingFilter.borrower = $scope.currentUser.id;
                $scope.filter();
            };


            $scope.filterByState = function () {
                $scope.filtered = true;
                $scope.filter();
            };

            $scope.filter = function() {
                $scope.$broadcast("startLoading", {parameters: [$scope.currentUser.id, $scope.stateFilter, $scope.bookingFilter.borrower, $scope.bookingFilter.owner], shouldReloadList: true});
            };

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