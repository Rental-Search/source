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

            $scope.currentUserUrl = "";
            $scope.bookingFilter = {};

            $scope.stateList = [
                {label: "Unpaid", value: "unpaid"},
                {label: "Authorized", value: "authorized"},
                {label: "Rejected", value: "rejected"},
                {label: "Pending", value: "pending"},
                {label: "Canceled", value: "canceled"},
                {label: "Ongoing", value: "ongoing"},
                {label: "Ended", value: "ended"},
                {label: "Closed", value: "closed"},
                {label: "Incident", value: "incident"}
            ];

            $scope.stateFilter = undefined;

            $scope.currentUserPromise.then(function (currentUser) {
                BookingsLoadService.getBookingList(undefined, currentUser.id).then(function (bookingList) {
                    $scope.bookingList = bookingList;
                    // Get current user url
                    $scope.currentUserUrl = Endpoints.api_url + "users/" + currentUser.id + "/";

                    // TODO Initiate custom scrollbars
                    //$scope.initCustomScrollbars();
                });
            });

            $scope.filterByOwner = function () {
                $scope.bookingFilter.owner = $scope.currentUserUrl;
                $scope.bookingFilter.borrower = undefined;
            };

            $scope.filterByBorrower = function () {
                $scope.bookingFilter.owner = undefined;
                $scope.bookingFilter.borrower = $scope.currentUserUrl;
            };

            $scope.filterByBoth = function () {
                $scope.bookingFilter.owner = undefined;
                $scope.bookingFilter.borrower = undefined;
            };

            $scope.filterByState = function () {
                $scope.bookingFilter.state = $scope.stateFilter;
            };
        }
    ]);
});