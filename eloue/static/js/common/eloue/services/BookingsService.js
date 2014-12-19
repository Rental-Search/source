"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Service for managing bookings.
     */
    EloueCommon.factory("BookingsService", [
        "$q",
        "Bookings",
        "UtilsService",
        function ($q, Bookings, UtilsService) {
            var bookingsService = {};

            bookingsService.getBookingsByProduct = function (productId) {
                var deferred = $q.defer();
                var bookingList = [];
                Bookings.get({product: productId, _cache: new Date().getTime()}).$promise.then(function (data) {

                    angular.forEach(data.results, function (value, key) {
                        var booking = {
                            state: value.state,
                            total_amount: value.total_amount,
                            uuid: value.uuid,
                            start_date: {
                                day: UtilsService.formatDate(value.started_at, "dd"),
                                month: UtilsService.formatDate(value.started_at, "MMMM"),
                                year: UtilsService.formatDate(value.started_at, "yyyy")
                            },
                            end_date: {
                                day: UtilsService.formatDate(value.ended_at, "dd"),
                                month: UtilsService.formatDate(value.ended_at, "MMMM"),
                                year: UtilsService.formatDate(value.ended_at, "yyyy")
                            }
                        };

                        booking.title = value.product.summary;
                        if (jQuery(value.product.pictures).size() > 0) {
                            booking.picture = value.product.pictures[0].image.thumbnail;
                        }
                        bookingList.push(booking);
                    });
                });
                deferred.resolve(bookingList);

                return deferred.promise;
            };

            return bookingsService;
        }
    ]);
});
