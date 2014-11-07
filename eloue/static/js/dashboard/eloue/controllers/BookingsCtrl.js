"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the bookings page.
     */
    angular.module("EloueDashboardApp").controller("BookingsCtrl", [
        "$scope",
        "$timeout",
        "UsersService",
        function ($scope, $timeout, UsersService) {
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

            if (!$scope.currentUserPromise) {
                $scope.currentUserPromise = UsersService.getMe().$promise;
            }
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

            // Timeout is used because of chosen issue (when options are loaded asynchronously, they sometimes not visible in chosen widget)
            $timeout(function () {
                $("#stateFilterSelect").chosen();
                $(".chosen-drop").mCustomScrollbar({
                    scrollInertia: '100',
                    autoHideScrollbar: true,
                    theme: 'dark-thin',
                    scrollbarPosition: 'outside',
                    advanced:{
                        autoScrollOnFocus: false,
                        updateOnContentResize: true
                    }
                });
            }, 500);

        }
    ]);
});