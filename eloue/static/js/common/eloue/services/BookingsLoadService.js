"use strict";
define(["../../../common/eloue/commonApp", "../../../common/eloue/resources", "../../../common/eloue/values",
    "../../../common/eloue/services/UtilsService",
    "../../../common/eloue/services/BookingsParseService",
    "../../../common/eloue/services/MessageThreadsService"], function (EloueCommon) {
    /**
     * Service for managing bookings.
     */
    EloueCommon.factory("BookingsLoadService", [
        "$q",
        "Endpoints",
        "Bookings",
        "UtilsService",
        "BookingsParseService",
        "MessageThreadsService",
        function ($q, Endpoints, Bookings, UtilsService, BookingsParseService, MessageThreadsService) {
            var bookingsLoadService = {};

            bookingsLoadService.getBookingList = function (author, state, borrowerId, ownerId, page) {
                var deferred = $q.defer();
                var params = {
                    page: page,
                    author: author,
                    ordering: "-created_at",
                    _cache: new Date().getTime()
                };
                if (!!state) {
                    params.state = state;
                }
                if (!!borrowerId) {
                    params.borrower = borrowerId;
                }
                if (!!ownerId) {
                    params.owner = ownerId;
                }

                // Load bookings
                Bookings.get(params).$promise.then(function (bookingListData) {
                    var bookingListPromises = [];

                    // For each booking
                    angular.forEach(bookingListData.results, function (bookingData, key) {
                        var bookingDeferred = $q.defer();

                        var booking = BookingsParseService.parseBookingListItem(bookingData, bookingData.product, bookingData.product.pictures);
                        bookingDeferred.resolve(booking);

                        bookingListPromises.push(bookingDeferred.promise);
                    });

                    $q.all(bookingListPromises).then(function (bookingList) {
                        deferred.resolve(
                            {
                                list: bookingList,
                                next: bookingListData.next
                            });
                    });
                });

                return deferred.promise;
            };

            bookingsLoadService.getBooking = function (bookingUUID) {
                var deferred = $q.defer();

                // Load booking
                Bookings.get({
                    uuid: bookingUUID,
                    _cache: new Date().getTime()
                }).$promise.then(function (bookingData) {
                        var booking = BookingsParseService.parseBooking(bookingData);
                        if (jQuery(bookingData.product.pictures).size() > 0) {
                            booking.product.picture = bookingData.product.pictures[0].image.thumbnail;
                        }
                        deferred.resolve(booking);
                    });

                return deferred.promise;
            };

            bookingsLoadService.getBookingDetails = function (bookingUUID) {
                var deferred = $q.defer();

                // Load booking
                this.getBooking(bookingUUID).then(function (booking) {
                    MessageThreadsService.getMessageThread(booking.product.id, booking.borrower.id).then(function (threads) {
                        if (threads && threads.length > 0) {
                            booking.lastThreadId = UtilsService.getIdFromUrl(threads[threads.length - 1].thread);
                        }
                        deferred.resolve(booking);
                    });
                });

                return deferred.promise;
            };

            bookingsLoadService.acceptBooking = function (uuid) {
                return Bookings.accept({uuid: uuid}, {uuid: uuid});
            };

            bookingsLoadService.cancelBooking = function (uuid) {
                return Bookings.cancel({uuid: uuid}, {uuid: uuid});
            };

            bookingsLoadService.rejectBooking = function (uuid) {
                return Bookings.reject({uuid: uuid}, {uuid: uuid});
            };

            bookingsLoadService.postIncident = function (uuid, description) {
                return Bookings.incident({uuid: uuid}, {description: description});
            };

            bookingsLoadService.downloadContract = function (uuid) {
                UtilsService.downloadPdfFile(Endpoints.api_url + "bookings/" + uuid + "/contract/", "contrat.pdf");
            };

            bookingsLoadService.getBookingByProduct = function (productId) {
                var deferred = $q.defer();

                // Load all bookings for this product
                Bookings.get({
                    product: productId,
                    _cache: new Date().getTime()
                }).$promise.then(function (bookingListData) {
                        var bookingsCount = bookingListData.results.length;
                        var booking = null;

                        if (bookingsCount > 0) {
                            var bookingData = bookingListData.results[bookingsCount - 1];
                            booking = BookingsParseService.parseBooking(bookingData);
                        }

                        deferred.resolve(booking);
                    });

                return deferred.promise;
            };

            bookingsLoadService.requestBooking = function (booking) {
                return Bookings.save(booking).$promise;
            };

            bookingsLoadService.payForBooking = function (uuid, paymentInfo) {
                return Bookings.pay({uuid: uuid}, paymentInfo).$promise;
            };
            return bookingsLoadService;
        }
    ]);
});
