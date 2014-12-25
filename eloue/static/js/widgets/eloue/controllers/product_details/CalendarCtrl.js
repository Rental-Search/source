define([
    "eloue/app",
    "../../../../common/eloue/services/BookingsService"
], function (EloueWidgetsApp) {
    /**
     * Controller for calendar tab on product details page (currently it is hidden).
     */
    "use strict";
    EloueWidgetsApp.controller("CalendarCtrl", [
        "$scope", "BookingsService",
        function ($scope, BookingsService) {
            $scope.selectedMonthAndYear = Date.today().getMonth() + " " + Date.today().getFullYear();
            $scope.showUnavailable = true;
            $scope.showBookings = true;
            $scope.weeks = {};
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

            /**
             * Used to load calendar with product booking data.
             */
            $scope.loadCalendar = function () {
                BookingsService.getBookingsByProduct($scope.product.id).then(function (bookings) {

                    angular.forEach(bookings, function (value) {
                        value.startDay = Date.parse(value.start_date.day + " " + value.start_date.month + " " + value.start_date.year);
                        value.endDay = Date.parse(value.end_date.day + " " + value.end_date.month + " " + value.end_date.year);
                    });
                    $scope.bookings = bookings;

                    $scope.updateCalendar();
                });
            };

            $scope.updateCalendar = function () {
                $scope.currentBookings = [];
                var s = $scope.selectedMonthAndYear.split(" "), date = new Date(), i, j, week, weeks = [],
                    start = new Date(date.moveToFirstDayOfMonth()), currentDay, days, isBooked;
                date.setMonth(s[0]);
                date.setFullYear(s[1]);
                for (i = 0; i < 6; i += 1) {
                    currentDay = start.moveToDayOfWeek(1, -1);
                    days = [];
                    for (j = 0; j < 7; j += 1) {
                        isBooked = false;
                        angular.forEach($scope.bookings, function (value) {
                            if (currentDay.between(value.startDay, value.endDay)) {
                                isBooked = true;
                                $scope.currentBookings.push(value);
                            }
                        });
                        days.push({dayOfMonth: currentDay.getDate(), isBooked: isBooked});
                        currentDay.add(1).days();
                    }
                    week = {};
                    week.weekDays = days;
                    weeks.push(week);
                    start.add(1).weeks();
                }
                $scope.weeks = weeks;
            };

            $scope.onShowUnavailable = function () {
            };

            $scope.onShowBookings = function () {
            };
        }
    ]);
});
