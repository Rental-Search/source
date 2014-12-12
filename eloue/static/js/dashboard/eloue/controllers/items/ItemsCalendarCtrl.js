"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items calendar tab.
     */
    angular.module("EloueDashboardApp").controller("ItemsCalendarCtrl", [
        "$scope",
        "$stateParams",
        "Endpoints",
        "BookingsService",
        "UnavailabilityPeriodsService",
        function ($scope, $stateParams, Endpoints, BookingsService, UnavailabilityPeriodsService) {

            $scope.selectedMonthAndYear = Date.today().getMonth()+ " " + Date.today().getFullYear();
            $scope.showUnavailable = true;
            $scope.showBookings = true;
            $scope.bookings = [];
            $scope.productUnavailablePeriods = [];
            $scope.weeks = {};
            $scope.newUnavailabilityPeriod = {};
            $scope.unavailabilityPeriodValidationError = "";

            var months = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"];

            $scope.monthOptions = [
                {name: months[Date.today().add(-1).months().getMonth()] + " " + Date.today().add(-1).months().getFullYear(), value: Date.today().add(-1).months().getMonth() + " " + Date.today().add(-1).months().getFullYear()},
                {name: months[Date.today().getMonth()] + " " + Date.today().getFullYear(), value: Date.today().getMonth() + " " + Date.today().getFullYear()},
                {name: months[Date.today().add(1).months().getMonth()] + " " + Date.today().add(1).months().getFullYear(), value: Date.today().add(1).months().getMonth() + " " + Date.today().add(1).months().getFullYear()},
                {name: months[Date.today().add(2).months().getMonth()] + " " + Date.today().add(2).months().getFullYear(), value: Date.today().add(2).months().getMonth() + " " + Date.today().add(2).months().getFullYear()},
                {name: months[Date.today().add(3).months().getMonth()] + " " + Date.today().add(3).months().getFullYear(), value: Date.today().add(3).months().getMonth() + " " + Date.today().add(3).months().getFullYear()},
                {name: months[Date.today().add(4).months().getMonth()] + " " + Date.today().add(4).months().getFullYear(), value: Date.today().add(4).months().getMonth() + " " + Date.today().add(4).months().getFullYear()},
                {name: months[Date.today().add(5).months().getMonth()] + " " + Date.today().add(5).months().getFullYear(), value: Date.today().add(5).months().getMonth() + " " + Date.today().add(5).months().getFullYear()},
                {name: months[Date.today().add(6).months().getMonth()] + " " + Date.today().add(6).months().getFullYear(), value: Date.today().add(6).months().getMonth() + " " + Date.today().add(6).months().getFullYear()},
                {name: months[Date.today().add(7).months().getMonth()] + " " + Date.today().add(7).months().getFullYear(), value: Date.today().add(7).months().getMonth() + " " + Date.today().add(7).months().getFullYear()},
                {name: months[Date.today().add(8).months().getMonth()] + " " + Date.today().add(8).months().getFullYear(), value: Date.today().add(8).months().getMonth() + " " + Date.today().add(8).months().getFullYear()},
                {name: months[Date.today().add(9).months().getMonth()] + " " + Date.today().add(9).months().getFullYear(), value: Date.today().add(9).months().getMonth() + " " + Date.today().add(9).months().getFullYear()},
                {name: months[Date.today().add(10).months().getMonth()] + " " + Date.today().add(10).months().getFullYear(), value: Date.today().add(10).months().getMonth() + " " + Date.today().add(10).months().getFullYear()},
                {name: months[Date.today().add(11).months().getMonth()] + " " + Date.today().add(11).months().getFullYear(), value: Date.today().add(11).months().getMonth() + " " + Date.today().add(11).months().getFullYear()},
                {name: months[Date.today().add(12).months().getMonth()] + " " + Date.today().add(12).months().getFullYear(), value: Date.today().add(12).months().getMonth() + " " + Date.today().add(12).months().getFullYear()}
            ];

            BookingsService.getBookingsByProduct($stateParams.id).then(function (bookings) {
                $scope.markListItemAsSelected("item-tab-", "calendar");
                angular.forEach(bookings, function (value, key) {
                    value.startDay = Date.parse(value.start_date.day + " " + value.start_date.month + " " + value.start_date.year);
                    value.endDay = Date.parse(value.end_date.day + " " + value.end_date.month + " " + value.end_date.year);
                });
                $scope.bookings = bookings;
                UnavailabilityPeriodsService.getByProduct($stateParams.id).then(function (periods) {
                    $scope.unavailablePeriods = periods.results;
                    angular.forEach($scope.unavailablePeriods, function (value, key) {
                        value.startDay = Date.parseExact(value.started_at, "yyyy-MM-ddTHH:mm:ss");
                        value.endDay = Date.parseExact(value.ended_at, "yyyy-MM-ddTHH:mm:ss");
                    });
                    $scope.updateCalendar();
                });
            });

            $scope.handleResponseErrors = function(error) {
                $scope.submitInProgress = false;
            };

            $scope.updateCalendar = function () {
                $scope.productUnavailablePeriods = [];
                var s = $scope.selectedMonthAndYear.split(" ");
                var date = new Date();
                date.setMonth(s[0]);
                date.setFullYear(s[1]);
                var weeks = [];
                var start = new Date(date.moveToFirstDayOfMonth());
                for (var i = 0; i < 6; i++) {
                    var currentDay = start.moveToDayOfWeek(1, -1);
                    var days = [];
                    for (var j = 0; j < 7; j++) {
                        var isBooked = false;
                        var isUnavailable = false;
                        angular.forEach($scope.bookings, function (value, key) {
                            if (currentDay.between(value.startDay, value.endDay)) {
                                isBooked = true;
                                value.reason = "booked";
                                if ($.inArray(value, $scope.productUnavailablePeriods) == -1) {
                                    $scope.productUnavailablePeriods.push(value);
                                }
                            }
                        });

                        angular.forEach($scope.unavailablePeriods, function (value, key) {
                            if (currentDay.between(value.startDay, value.endDay)) {
                                isUnavailable = true;
                                value.reason = "unavailable";
                                if ($.inArray(value, $scope.productUnavailablePeriods) == -1) {
                                    $scope.productUnavailablePeriods.push(value);
                                }
                            }
                        });

                        days.push({dayOfMonth: currentDay.getDate(), isBooked: isBooked, isUnavailable: isUnavailable});
                        currentDay.add(1).days();
                    }

                    var week = {};
                    week.weekDays = days;
                    weeks.push(week);
                    start.add(1).weeks();
                }
                $scope.weeks = weeks;
            };

            $scope.onShowUnavailable = function () {
                console.log("onShowUnavailable");
            };

            $scope.onShowBookings = function () {
                console.log("onShowBookings");
            };

            $scope.showAddPeriodForm = function() {
                $("#add-period").modal();
            };

            $scope.saveUnavailabilityPeriod = function() {
                if ($scope.validateUnavailabilityPeriod()) {
                    console.log("saveUnavailabilityPeriod");
                    console.log($scope.newUnavailabilityPeriod);
                    $scope.submitInProgress = true;
                    var startDate = Date.parseExact($scope.newUnavailabilityPeriod.started_at, "dd/MM/yyyy"),
                        endDate = Date.parseExact($scope.newUnavailabilityPeriod.ended_at, "dd/MM/yyyy");
                    $scope.newUnavailabilityPeriod.started_at = startDate.toString("yyyy-MM-dd HH:mm:ss");
                    $scope.newUnavailabilityPeriod.ended_at = endDate.toString("yyyy-MM-dd HH:mm:ss");
                    $scope.newUnavailabilityPeriod.product = Endpoints.api_url + "products/" + $stateParams.id + "/";

                    UnavailabilityPeriodsService.savePeriod($scope.newUnavailabilityPeriod).$promise.then(function (result) {
                        $scope.updateCalendar();
                        $("#add-period").modal('hide');
                        $scope.newUnavailabilityPeriod = {};
                        $scope.submitInProgress = false;
                    }, function (error) {
                        $scope.handleResponseErrors(error);
                    });
                }
            };

            $scope.validateUnavailabilityPeriod = function() {
                //TODO: The user can't create an unavailability period if the product is already booked
                // TODO: The user can't create an unavailability period if the start or end date is between an other unavailability period.
                return true;
            };
        }]);
});