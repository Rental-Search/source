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
            $scope.bookingList = [];
            $scope.stateFilter = undefined;

            $scope.currentUserPromise.then(function (currentUser) {
                $scope.currentUserUrl = Endpoints.api_url + "users/" + currentUser.id + "/";

                $scope.$broadcast("startLoading", {parameters: [$scope.currentUser.id], shouldReloadList: true});
//                BookingsLoadService.getBookingList($scope.page, currentUser.id).then(function (bookingList) {
//                    $scope.bookingList = bookingList;
//                    // Get current user url
//
//
//                    // TODO Initiate custom scrollbars
//                    //$scope.initCustomScrollbars();
//                });
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

            //TODO: add all possible states
            $scope.getStateClass = function(state) {
                switch (state) {
                    case "pending":
                        return "soon";
                    case "ongoing":
                        return "in-progress";
                    case "ended":
                        return "completed";
                    default:
                        return "in-progress"
                }
            };
        }
    ]);
});