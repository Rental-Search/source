define(["../../../common/eloue/commonApp", "../../../common/eloue/resources", "../../../common/eloue/values",
    "../../../common/eloue/services/UtilsService",
    "../../../common/eloue/services/MessageThreadsService"
], function (EloueCommon) {
    "use strict";
    /**
     * Service for managing bookings.
     */
    EloueCommon.factory("BookingsService", [
        "$q",
        "Endpoints",
        "Bookings",
        "UtilsService",
        "MessageThreadsService",
        function ($q, Endpoints, Bookings, UtilsService, MessageThreadsService) {
            var bookingsService = {};

            bookingsService.getBookingsByProduct = function (productId) {
                var deferred = $q.defer(), bookingList = [];
                Bookings.get({product: productId, _cache: new Date().getTime()}).$promise.then(function (data) {

                    angular.forEach(data.results, function (value) {
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

            bookingsService.getBookingList = function (author, state, borrowerId, ownerId, page) {
                var deferred = $q.defer();
                var params = {
                    page: page,
                    author: author,
                    ordering: "-created_at",
                    _cache: new Date().getTime()
                };
                if (state) {
                    params.state = state;
                }
                if (borrowerId) {
                    params.borrower = borrowerId;
                }
                if (ownerId) {
                    params.owner = ownerId;
                }

                // Load bookings
                Bookings.get(params).$promise.then(function (bookingListData) {
                    var bookingListPromises = [];

                    // For each booking
                    angular.forEach(bookingListData.results, function (bookingData, key) {
                        var bookingDeferred = $q.defer();

                        var booking = bookingsService.parseBookingListItem(bookingData, bookingData.product, bookingData.product.pictures);
                        bookingDeferred.resolve(booking);

                        bookingListPromises.push(bookingDeferred.promise);
                    });

                    $q.all(bookingListPromises).then(function (bookingList) {
                        deferred.resolve(
                            {
                                list: bookingList,
                                next: bookingListData.next
                            }
                        );
                    });
                });

                return deferred.promise;
            };

            bookingsService.getBooking = function (bookingUUID) {
                var deferred = $q.defer();

                // Load booking
                Bookings.get({
                    uuid: bookingUUID,
                    _cache: new Date().getTime()
                }).$promise.then(
                    function (bookingData) {
                        var booking = bookingsService.parseBooking(bookingData);
                        if (jQuery(bookingData.product.pictures).size() > 0) {
                            booking.product.picture = bookingData.product.pictures[0].image.thumbnail;
                        }
                        deferred.resolve(booking);
                    }
                );

                return deferred.promise;
            };

            bookingsService.getBookingDetails = function (bookingUUID) {
                var deferred = $q.defer();

                // Load booking
                this.getBooking(bookingUUID).then(function (booking) {
                    MessageThreadsService.getMessageThreadByProductAndParticipant(booking.product.id, booking.borrower.id).then(function (threads) {
                        if (threads.threads && threads.threads.results.length > 0) {
                            booking.lastThreadId = threads.threads.results[threads.threads.results.length - 1].id;
                        }
                        deferred.resolve(booking);
                    });
                });

                return deferred.promise;
            };

            bookingsService.acceptBooking = function (uuid) {
                return Bookings.accept({uuid: uuid}, {uuid: uuid}).$promise;
            };

            bookingsService.cancelBooking = function (uuid) {
                return Bookings.cancel({uuid: uuid}, {uuid: uuid}).$promise;
            };

            bookingsService.rejectBooking = function (uuid) {
                return Bookings.reject({uuid: uuid}, {uuid: uuid}).$promise;
            };

            bookingsService.postIncident = function (uuid, description) {
                return Bookings.incident({uuid: uuid}, {description: description}).$promise;
            };

            bookingsService.downloadContract = function (uuid) {
                UtilsService.downloadPdfFile(Endpoints.api_url + "bookings/" + uuid + "/contract/", "contrat.pdf");
            };

            bookingsService.getBookingByProduct = function (productId) {
                var deferred = $q.defer();

                // Load all bookings for this product
                Bookings.get({
                    product: productId,
                    _cache: new Date().getTime()
                }).$promise.then(
                    function (bookingListData) {
                        var bookingsCount = bookingListData.results.length, booking = null, bookingData;

                        if (bookingsCount > 0) {
                            bookingData = bookingListData.results[bookingsCount - 1];
                            booking = bookingsService.parseBooking(bookingData);
                        }

                        deferred.resolve(booking);
                    },
                    function (reason) {
                        deferred.reject(reason);
                    }
                );

                return deferred.promise;
            };

            bookingsService.requestBooking = function (booking) {
                return Bookings.save(booking).$promise;
            };

            bookingsService.payForBooking = function (uuid, paymentInfo) {
                return Bookings.pay({uuid: uuid}, paymentInfo).$promise;
            };

            bookingsService.parseBookingListItem = function (bookingData, productData, picturesDataArray) {
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

            bookingsService.parseBooking = function (bookingData) {
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

            return bookingsService;
        }
    ]);
});
