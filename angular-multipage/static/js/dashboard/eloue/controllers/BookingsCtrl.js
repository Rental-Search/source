"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the bookings page.
     */
    angular.module("EloueDashboardApp").controller("BookingsCtrl", [
        "$q",
        "$scope",
        "Endpoints",
        "BookingsLoadService",
        function ($q, $scope, Endpoints, BookingsLoadService) {
            var promises = {
                currentUser: $scope.currentUserPromise,
                bookingList: BookingsLoadService.getBookingList()
            };

            $q.all(promises).then(function (results) {
                $scope.bookingList = results.bookingList;
                $scope.bookingFilter = {};

                // Get current user url
                var currentUserUrl = Endpoints.api_url + "users/" + results.currentUser.id + "/";

                $scope.filterByOwner = function () {
                    $scope.bookingFilter.owner = currentUserUrl;
                    $scope.bookingFilter.borrower = undefined;
                };

                $scope.filterByBorrower = function () {
                    $scope.bookingFilter.owner = undefined;
                    $scope.bookingFilter.borrower = currentUserUrl;
                };

                $scope.filterByBoth = function () {
                    $scope.bookingFilter.owner = undefined;
                    $scope.bookingFilter.borrower = undefined;
                };

                // Initiate custom scrollbars
                $scope.initCustomScrollbars();
            });
        }
    ]);
});