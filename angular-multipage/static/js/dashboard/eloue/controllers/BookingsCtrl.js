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

                $scope.stateList = [
                    {label: "Statut", value: undefined},
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

                $scope.stateFilter = $scope.stateList[0].value;

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

                $scope.filterByState = function () {
                    $scope.bookingFilter.state = $scope.stateFilter;
                };

                // TODO Initiate custom scrollbars
                //$scope.initCustomScrollbars();
            });
        }
    ]);
});