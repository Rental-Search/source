"use strict";
define(["../../../common/eloue/commonApp", "../../../common/eloue/services/UtilsService"], function (EloueCommon) {
    /**
     * Service for parsing bookings.
     */
    EloueCommon.factory("BookingsParseService", [
        "UtilsService",
        function (UtilsService) {
            var bookingsParseService = {};

            bookingsParseService.parseBookingListItem = function (bookingData, productData, picturesDataArray) {
                var bookingResult = angular.copy(bookingData);

                // Parse dates
                bookingResult.start_date = {
                    day: UtilsService.formatDate(bookingResult.started_at, "dd"),
                    month: UtilsService.formatDate(bookingResult.started_at, "MMMM"),
                    year: UtilsService.formatDate(bookingResult.started_at, "yyyy")
                };

                bookingResult.end_date = {
                    day: UtilsService.formatDate(bookingResult.ended_at, "dd"),
                    month: UtilsService.formatDate(bookingResult.ended_at, "MMMM"),
                    year: UtilsService.formatDate(bookingResult.ended_at, "yyyy")
                };

                // Parse product
                bookingResult.product = productData;

                // Parse pictures
                if (angular.isArray(picturesDataArray) && picturesDataArray.length > 0) {
                    bookingResult.picture = picturesDataArray[0].image.thumbnail;
                }

                return bookingResult;
            };

            bookingsParseService.parseBooking = function (bookingData) {
                var bookingResult = angular.copy(bookingData);

                // Parse dates
                bookingResult.start_date = {
                    week_day: UtilsService.formatDate(bookingResult.started_at, "EEEE"),
                    day: UtilsService.formatDate(bookingResult.started_at, "dd"),
                    month: UtilsService.formatDate(bookingResult.started_at, "MMMM"),
                    year: UtilsService.formatDate(bookingResult.started_at, "yyyy")
                };

                bookingResult.end_date = {
                    week_day: UtilsService.formatDate(bookingResult.ended_at, "EEEE"),
                    day: UtilsService.formatDate(bookingResult.ended_at, "dd"),
                    month: UtilsService.formatDate(bookingResult.ended_at, "MMMM"),
                    year: UtilsService.formatDate(bookingResult.ended_at, "yyyy")
                };

                bookingResult.start_time = UtilsService.formatDate(bookingResult.started_at, "HH'h'mm");
                bookingResult.end_time = UtilsService.formatDate(bookingResult.ended_at, "HH'h'mm");

                // Parse period
                var period = UtilsService.calculatePeriodBetweenDates(bookingResult.started_at, bookingResult.ended_at);

                bookingResult.period_days = period.period_days;
                bookingResult.period_hours = period.period_hours;

                return bookingResult;
            };

            return bookingsParseService;
        }
    ]);
});
