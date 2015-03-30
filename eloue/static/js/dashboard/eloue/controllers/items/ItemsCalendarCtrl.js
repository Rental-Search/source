define([
    "eloue/app",
    "../../../../common/eloue/values",
    "../../../../common/eloue/services/BookingsService",
    "../../../../common/eloue/services/UnavailabilityPeriodsService"
], function (EloueDashboardApp) {
    "use strict";
    /**
     * Controller for the items calendar tab.
     */
    EloueDashboardApp.controller("ItemsCalendarCtrl", [
        "$scope",
        "$stateParams",
        "Endpoints",
        "BookingsService",
        "UnavailabilityPeriodsService",
        function ($scope, $stateParams, Endpoints, BookingsService, UnavailabilityPeriodsService) {

            $scope.selectedMonthAndYear = Date.today().getMonth() + " " + Date.today().getFullYear();
            $scope.showUnavailable = true;
            $scope.showBookings = true;
            $scope.bookings = [];
            $scope.productUnavailablePeriods = [];
            $scope.weeks = {};
            $scope.newUnavailabilityPeriod = {quantity: 1};
            $scope.unavailabilityPeriodValidationError = "";

            var months = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"];

            $scope.monthOptions = [
                {
                    name: months[Date.today().add(-1).months().getMonth()] + " " + Date.today().add(-1).months().getFullYear(),
                    value: Date.today().add(-1).months().getMonth() + " " + Date.today().add(-1).months().getFullYear()
                },
                {
                    name: months[Date.today().getMonth()] + " " + Date.today().getFullYear(),
                    value: Date.today().getMonth() + " " + Date.today().getFullYear()
                },
                {
                    name: months[Date.today().add(1).months().getMonth()] + " " + Date.today().add(1).months().getFullYear(),
                    value: Date.today().add(1).months().getMonth() + " " + Date.today().add(1).months().getFullYear()
                },
                {
                    name: months[Date.today().add(2).months().getMonth()] + " " + Date.today().add(2).months().getFullYear(),
                    value: Date.today().add(2).months().getMonth() + " " + Date.today().add(2).months().getFullYear()
                },
                {
                    name: months[Date.today().add(3).months().getMonth()] + " " + Date.today().add(3).months().getFullYear(),
                    value: Date.today().add(3).months().getMonth() + " " + Date.today().add(3).months().getFullYear()
                },
                {
                    name: months[Date.today().add(4).months().getMonth()] + " " + Date.today().add(4).months().getFullYear(),
                    value: Date.today().add(4).months().getMonth() + " " + Date.today().add(4).months().getFullYear()
                },
                {
                    name: months[Date.today().add(5).months().getMonth()] + " " + Date.today().add(5).months().getFullYear(),
                    value: Date.today().add(5).months().getMonth() + " " + Date.today().add(5).months().getFullYear()
                },
                {
                    name: months[Date.today().add(6).months().getMonth()] + " " + Date.today().add(6).months().getFullYear(),
                    value: Date.today().add(6).months().getMonth() + " " + Date.today().add(6).months().getFullYear()
                },
                {
                    name: months[Date.today().add(7).months().getMonth()] + " " + Date.today().add(7).months().getFullYear(),
                    value: Date.today().add(7).months().getMonth() + " " + Date.today().add(7).months().getFullYear()
                },
                {
                    name: months[Date.today().add(8).months().getMonth()] + " " + Date.today().add(8).months().getFullYear(),
                    value: Date.today().add(8).months().getMonth() + " " + Date.today().add(8).months().getFullYear()
                },
                {
                    name: months[Date.today().add(9).months().getMonth()] + " " + Date.today().add(9).months().getFullYear(),
                    value: Date.today().add(9).months().getMonth() + " " + Date.today().add(9).months().getFullYear()
                },
                {
                    name: months[Date.today().add(10).months().getMonth()] + " " + Date.today().add(10).months().getFullYear(),
                    value: Date.today().add(10).months().getMonth() + " " + Date.today().add(10).months().getFullYear()
                },
                {
                    name: months[Date.today().add(11).months().getMonth()] + " " + Date.today().add(11).months().getFullYear(),
                    value: Date.today().add(11).months().getMonth() + " " + Date.today().add(11).months().getFullYear()
                },
                {
                    name: months[Date.today().add(12).months().getMonth()] + " " + Date.today().add(12).months().getFullYear(),
                    value: Date.today().add(12).months().getMonth() + " " + Date.today().add(12).months().getFullYear()
                }
            ];

            BookingsService.getBookingsByProduct($stateParams.id).then(function (bookings) {
                $scope.markListItemAsSelected("item-tab-", "calendar");
                angular.forEach(bookings, function (value) {
                    value.startDay = Date.parse(value.start_date.day + " " + value.start_date.month + " " + value.start_date.year);
                    value.endDay = Date.parse(value.end_date.day + " " + value.end_date.month + " " + value.end_date.year);
                });
                $scope.bookings = bookings;
                $scope.updateUnavailabilityPeriods();
            });

            $scope.updateUnavailabilityPeriods = function () {
                UnavailabilityPeriodsService.getByProduct($stateParams.id).then(function (periods) {
                    $scope.unavailablePeriods = periods.results;
                    angular.forEach($scope.unavailablePeriods, function (value, key) {
                        value.startDay = Date.parseExact(value.started_at, "yyyy-MM-ddTHH:mm:ss");
                        value.endDay = Date.parseExact(value.ended_at, "yyyy-MM-ddTHH:mm:ss");
                    });
                    $scope.updateCalendar();
                });
            };

            $scope.handleResponseErrors = function (error) {
                $scope.submitInProgress = false;
            };

            $scope.updateCalendar = function () {
                $scope.productUnavailablePeriods = [];
                var s = $scope.selectedMonthAndYear.split(" "), date = new Date(), weeks = [], start, i, j, currentDay,
                    days, isBooked, isUnavailable, week;
                date.setMonth(s[0]);
                date.setFullYear(s[1]);
                start = new Date(date.moveToFirstDayOfMonth());
                start.clearTime();
                for (i = 0; i < 6; i += 1) {
                    currentDay = start.moveToDayOfWeek(1, -1);
                    days = [];
                    for (j = 0; j < 7; j += 1) {
                        isBooked = false;
                        isUnavailable = false;
                        angular.forEach($scope.bookings, function (value) {
                            if (currentDay.between(value.startDay, value.endDay)) {
                                isBooked = true;
                                value.reason = "booked";
                                if ($.inArray(value, $scope.productUnavailablePeriods) === -1) {
                                    $scope.productUnavailablePeriods.push(value);
                                }
                            }
                        });

                        angular.forEach($scope.unavailablePeriods, function (value, key) {
                            if (currentDay.between(value.startDay, value.endDay)) {
                                isUnavailable = true;
                                value.reason = "unavailable";
                                if ($.inArray(value, $scope.productUnavailablePeriods) === -1) {
                                    $scope.productUnavailablePeriods.push(value);
                                }
                            }
                        });

                        days.push({dayOfMonth: currentDay.getDate(), isBooked: isBooked, isUnavailable: isUnavailable});
                        currentDay.add(1).days();
                    }
                    week = {};
                    week.weekDays = days;
                    weeks.push(week);
                    start.add(1).weeks();
                }
                $scope.weeks = weeks;
            };

            $scope.onShowUnavailable = function () {};

            $scope.onShowBookings = function () {};

            $scope.showAddPeriodForm = function () {
                $("#add-period").modal();
            };

            $scope.showUpdatePeriodForm = function (period) {
                $scope.newUnavailabilityPeriod.id = period.id;
                $scope.newUnavailabilityPeriod.started_at = Date.parseExact(period.started_at, "yyyy-MM-ddTHH:mm:ss").toString("dd/MM/yyyy");
                $scope.newUnavailabilityPeriod.ended_at = Date.parseExact(period.ended_at, "yyyy-MM-ddTHH:mm:ss").toString("dd/MM/yyyy");
                $scope.newUnavailabilityPeriod.quantity = period.quantity;
                $("#add-period").modal();
            };

            $scope.showConfirmForm = function (period) {
                $scope.selectedPeriod = period;
                $("#confirm-delete-period").modal();
            };

            $scope.saveUnavailabilityPeriod = function () {
                var initialStartDateStr = angular.copy($scope.newUnavailabilityPeriod.started_at), startDate = Date.parseExact(initialStartDateStr, "dd/MM/yyyy"),
                    initialEndDateStr = angular.copy($scope.newUnavailabilityPeriod.ended_at), endDate = Date.parseExact(initialEndDateStr, "dd/MM/yyyy");
                if ($scope.validateUnavailabilityPeriod(startDate, endDate)) {
                    $scope.submitInProgress = true;
                    $scope.newUnavailabilityPeriod.started_at = startDate.toString("yyyy-MM-dd HH:mm:ss");
                    $scope.newUnavailabilityPeriod.ended_at = endDate.toString("yyyy-MM-dd HH:mm:ss");
                    $scope.newUnavailabilityPeriod.product = Endpoints.api_url + "products/" + $stateParams.id + "/";
                    var promise = null;
                    if (!$scope.newUnavailabilityPeriod.id) {
                        promise = UnavailabilityPeriodsService.savePeriod($scope.newUnavailabilityPeriod);
                    } else {
                        promise = UnavailabilityPeriodsService.updatePeriod($scope.newUnavailabilityPeriod);
                    }
                    promise.then(function () {
                        $scope.updateCalendar();
                        $("#add-period").modal("hide");
                        $scope.newUnavailabilityPeriod = {};
                        $scope.submitInProgress = false;
                        $scope.unavailabilityPeriodValidationError = "";
                        $scope.updateUnavailabilityPeriods();
                    }, function (error) {
                        $scope.newUnavailabilityPeriod.started_at = initialStartDateStr;
                        $scope.newUnavailabilityPeriod.ended_at = initialEndDateStr;
                        $scope.handleResponseErrors(error);
                    });
                }
            };

            $scope.validateUnavailabilityPeriod = function (startDate, endDate) {
                $scope.unavailabilityPeriodValidationError = "";
                var i, msPerDay = 1000 * 60 * 60 * 24,
                    dayDiff = Math.floor((endDate.getTime() - startDate.getTime()) / msPerDay),
                    start = angular.copy(endDate).add(1).days();
                start.clearTime();
                for (i = 0; i <= dayDiff; i += 1) {
                    var currentDay = start.add(-1).days();

                    angular.forEach($scope.bookings, function (value) {
                        if (currentDay.between(value.startDay, value.endDay)) {
                            $scope.unavailabilityPeriodValidationError = "La période d'indisponibilité n'a pas pu être créée car le produit est loué pendant cette période";
                        }
                    });

                    angular.forEach($scope.unavailablePeriods, function (value) {
                        if (currentDay.between(value.startDay, value.endDay)) {
                            if (!$scope.newUnavailabilityPeriod.id || $scope.newUnavailabilityPeriod.id !== value.id) {
                                $scope.unavailabilityPeriodValidationError = "La période d'indisponibilité n'a pas pu être créée car il existe déjà une période d'indisponibilité entre ces dates";
                            }
                        }
                    });
                    if ($scope.unavailabilityPeriodValidationError) {
                        return false;
                    }
                }
                return true;
            };

            $scope.deleteUnavailabilityPeriod = function (period) {
                UnavailabilityPeriodsService.deletePeriod(period).then(function () {
                    $scope.updateUnavailabilityPeriods();
                });
            };
        }]);
});
