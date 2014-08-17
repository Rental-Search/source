"use strict";
define(["../../common/eloue/commonApp", "../../common/eloue/resources", "../../common/eloue/values"],
    function (EloueCommon) {

        /**
         * Service for uploading forms.
         */
        EloueCommon.factory("FormService", [function () {
            var formService = {};

            formService.send = function (method, url, $form, successCallback, errorCallback) {
                $form.ajaxSubmit({
                    type: method,
                    url: url,
                    success: successCallback,
                    error: errorCallback
                });
            };

            return formService;
        }]);

        /**
         * Service for managing users.
         */
        EloueCommon.factory("UsersService", ["$q", "Users", "FormService", "Endpoints",
            function ($q, Users, FormService, Endpoints) {
                var usersService = {};

                usersService.get = function (userId, successCallback, errorCallback) {
                    return Users.get({id: userId}, successCallback, errorCallback);
                };

                usersService.getMe = function (successCallback, errorCallback) {
                    return Users.getMe({_cache: new Date().getTime()}, successCallback, errorCallback);
                };

                usersService.sendForm = function (userId, form, successCallback, errorCallback) {
                    // Calculate current user url
                    var currentUserUrl = Endpoints.api_url + "users/" + userId + "/";

                    // Send form to the current user url
                    FormService.send("POST", currentUserUrl, form, successCallback, errorCallback);
                };

                usersService.resetPassword = function (form) {
                    var resetPasswordUrl = Endpoints.api_url + "users/reset_password/";
                    var deferred = $q.defer();

                    FormService.send("POST", resetPasswordUrl, form,
                        function (data) {
                            deferred.resolve(data);
                        },
                        function (reason) {
                            deferred.reject(reason);
                        });

                    return deferred.promise;
                };

                return usersService;
            }
        ]);

        /**
         * Service for managing message threads.
         */
        EloueCommon.factory("MessageThreadsService", [
            "$q",
            "$filter",
            "MessageThreads",
            "Bookings",
            "ProductRelatedMessagesService",
            "UsersService",
            "ProductsService",
            "BookingsService",
            "UtilsService",
            function ($q, $filter, MessageThreads, Bookings, ProductRelatedMessagesService, UsersService, ProductsService, BookingsService, UtilsService) {
                var messageThreadsService = {};

                /**
                 * Retrieves list of message threads.
                 *
                 * @returns list of message threads
                 */
                messageThreadsService.getMessageThreads = function () {
                    var self = this;
                    var deferred = $q.defer();

                    MessageThreads.get({_cache: new Date().getTime()}).$promise.then(function (threads) {
                        var promises = [];

                        // For each message thread
                        angular.forEach(threads.results, function (value, key) {
                            var result = {
                                id: value.id,
                                subject: value.subject
                            };

                            var threadDeferred = $q.defer();
                            var threadPromises = {};

                            if (!value.last_message) {
                                result.message = "";
                                result.date = "";
                            } else {
                                // Get last message
                                var messageId = self.getIdFromUrl(value.last_message);
                                threadPromises.lastMessage = ProductRelatedMessagesService.getMessage(messageId).$promise;
                            }

                            // Get sender
                            // TODO probably the field needs to be changed
                            var senderId = self.getIdFromUrl(value.sender);
                            threadPromises.sender = UsersService.get(senderId).$promise;

                            // Set information in the result object
                            $q.all(threadPromises).then(function (threadResults) {
                                if (!!threadResults.lastMessage) {
                                    result.message = threadResults.lastMessage.body;
                                    result.date = UtilsService.formatDate(threadResults.lastMessage.sent_at, "HH'h'mm");
                                }
                                result.icon = threadResults.sender.avatar.thumbnail;
                                result.username = threadResults.sender.username;

                                threadDeferred.resolve(result);
                            });
                            promises.push(threadDeferred.promise);
                        });

                        $q.all(promises).then(function (results) {
                            deferred.resolve(results);
                        });
                    });

                    return deferred.promise;
                };

                /**
                 * Retrieves thread's data.
                 *
                 * @param threadId identifier of a thread
                 */
                messageThreadsService.getThread = function (threadId) {
                    var deferred = $q.defer();

                    // Send a request for a thread
                    MessageThreads.get({id: threadId, _cache: new Date().getTime()}).$promise.then(function (thread) {
                        var rootPromises = {};

                        // Get message list
                        var messagePromises = [];
                        angular.forEach(thread.messages, function (value, key) {
                            var messageDeferred = $q.defer();

                            // Get message
                            var messageId = UtilsService.getIdFromUrl(value);
                            ProductRelatedMessagesService.getMessage(messageId).$promise.then(function (data) {
                                var result = {
                                    id: data.id,
                                    body: data.body,
                                    date: UtilsService.formatDate(data.sent_at, "dd.mm.yyyy HH'h'mm")
                                };

                                // Get sender
                                var senderId = UtilsService.getIdFromUrl(data.sender);
                                UsersService.get(senderId).$promise.then(function (sender) {
                                    result.username = sender.username;
                                    result.icon = sender.avatar.thumbnail;
                                    messageDeferred.resolve(result);
                                });
                            });

                            messagePromises.push(messageDeferred.promise);
                        });
                        rootPromises.messages = $q.all(messagePromises);

                        // Get product
                        if (!!thread.product) {
                            var productDeferred = $q.defer();

                            var productId = UtilsService.getIdFromUrl(thread.product);
                            Bookings.get({product: productId}).$promise.then(function (data) {
                                if ($.isArray(data.results) && (data.results.length > 0)) {
                                    var bookingData = data.results[0];
                                    BookingsService.parseBookingDetail(bookingData, function (booking) {
                                        productDeferred.resolve(booking);
                                    });
                                }
                            });

                            rootPromises.product = productDeferred.promise;
                        }

                        $q.all(rootPromises).then(function (results) {
                            var result = {
                                users: [],
                                messages: results.messages,
                                product: results.product
                            };

                            // Push ids of users from a conversation
                            result.users.push(UtilsService.getIdFromUrl(thread.sender));
                            if (!!thread.recipient) {
                                result.users.push(UtilsService.getIdFromUrl(thread.recipient));
                            }

                            deferred.resolve(result);
                        });
                    });

                    return deferred.promise;
                };

                /**
                 * Retrieves list messages for a specific thread.
                 *
                 * @param threadId identifier of a thread
                 */
                messageThreadsService.getMessages = function (threadId) {
                    var self = this;
                    var deferred = $q.defer();

                    MessageThreads.get({id: threadId, _cache: new Date().getTime()}).$promise.then(function (thread) {
                        var promises = [];

                        // For each message
                        angular.forEach(thread.messages, function (value, key) {
                            var messageDeferred = $q.defer();

                            // Get message
                            var messageId = self.getIdFromUrl(value);
                            ProductRelatedMessagesService.getMessage(messageId).$promise.then(function (data) {
                                var result = {
                                    id: data.id,
                                    body: data.body,
                                    date: UtilsService.formatMessageDate(data.sent_at,
                                        "HH'h'mm", "dd.mm.yyyy HH'h'mm")
                                };

                                // Get sender
                                var senderId = self.getIdFromUrl(data.sender);
                                UsersService.get(senderId).$promise.then(function (sender) {
                                    result.username = sender.username;
                                    result.icon = sender.avatar.thumbnail;
                                    messageDeferred.resolve(result);
                                });
                            });

                            promises.push(messageDeferred.promise);
                        });

                        $q.all(promises).then(function (results) {
                            var result = {
                                users: [],
                                messages: results
                            };

                            // Push ids of users from a conversation
                            result.users.push(self.getIdFromUrl(thread.sender));
                            if (!!thread.recipient) {
                                result.users.push(self.getIdFromUrl(thread.recipient));
                            }

                            deferred.resolve(result);
                        });
                    });

                    return deferred.promise;
                };

                /**
                 * Retrieves identifier of the object from provided url, that ends with "../{%ID%}/"
                 * @param url URL
                 * @returns ID
                 */
                messageThreadsService.getIdFromUrl = function (url) {
                    var trimmedUrl = url.slice(0, url.length - 1);
                    return trimmedUrl.substring(trimmedUrl.lastIndexOf("/") + 1, url.length);
                };

                return messageThreadsService;
            }
        ]);

        /**
         * Service for managing product related messages.
         */
        EloueCommon.factory("ProductRelatedMessagesService", [
            "ProductRelatedMessages",
            "Endpoints",
            function (ProductRelatedMessages, Endpoints) {
                var productRelatedMessagesService = {};

                productRelatedMessagesService.getMessage = function (id) {
                    return ProductRelatedMessages.get({id: id, _cache: new Date().getTime()});
                };

                productRelatedMessagesService.postMessage = function (threadId, recipientId, text, offerid) {
                    var message = {
                        thread: Endpoints.api_url + "messagethreads/" + threadId + "/",
                        recipient: Endpoints.api_url + "users/" + recipientId + "/",
                        body: (!!text) ? text : "",
                        offer: (!!offerid) ? Endpoints.api_url + "bookings/" + offerid + "/" : null
                    };

                    return new ProductRelatedMessages(message).$save();
                };

                return productRelatedMessagesService;
            }
        ]);

        /**
         * Service for managing products.
         */
        EloueCommon.factory("ProductsService", ["Products", function (Products) {
            var productsService = {};

            productsService.getProduct = function (id) {
                return Products.get({id: id});
            };

            return productsService;
        }]);

        /**
         * Utils service.
         */
        EloueCommon.factory("UtilsService", ["$filter", function ($filter) {
            var utilsService = {};

            utilsService.formatDate = function (date, format) {
                return $filter("date")(date, format);
            };

            utilsService.formatMessageDate = function (dateString, shortFormat, fullFormat) {
                var sentDate = new Date(dateString);
                var nowDate = new Date();
                var dateFormat;

                // If date is today
                if (sentDate.setHours(0, 0, 0, 0) === nowDate.setHours(0, 0, 0, 0)) {
                    dateFormat = shortFormat;
                } else {
                    dateFormat = fullFormat;
                }
                return this.formatDate(dateString, dateFormat);
            };

            utilsService.getIdFromUrl = function (url) {
                var trimmedUrl = url.slice(0, url.length - 1);
                return trimmedUrl.substring(trimmedUrl.lastIndexOf("/") + 1, url.length);
            };

            return utilsService;
        }]);

        /**
         * Service for managing bookings.
         */
        EloueCommon.factory("BookingsService", [
            "$q",
            "Bookings",
            "ProductsService",
            "PicturesService",
            "AddressesService",
            "UsersService",
            "PhoneNumbersService",
            "UtilsService",
            function ($q, Bookings, ProductsService, PicturesService, AddressesService, UsersService, PhoneNumbersService, UtilsService) {
                var bookingsService = {};

                bookingsService.getBookings = function (page) {
                    var deferred = $q.defer();

                    Bookings.get({page: page}).$promise.then(function (data) {
                        var promises = [];

                        angular.forEach(data.results, function (value, key) {
                            var bookingDeferred = $q.defer();
                            var booking = {
                                state: value.state,
                                total_amount: value.total_amount,
                                uuid: value.uuid,
                                start_date: UtilsService.formatDate(value.started_at, "dd MMMM yyyy"),
                                end_date: UtilsService.formatDate(value.ended_at, "dd MMMM yyyy")
                            };

                            var bookingPromises = {};

                            // Get product id
                            var productId = UtilsService.getIdFromUrl(value.product);

                            // Get product
                            bookingPromises.product = ProductsService.getProduct(productId).$promise;

                            // Get picture
                            bookingPromises.pictures = PicturesService.getPicturesByProduct(productId).$promise;

                            $q.all(bookingPromises).then(function (results) {
                                booking.title = results.product.summary;
                                if (jQuery(results.pictures.results).size() > 0) {
                                    booking.picture = results.pictures.results[0].image.thumbnail;
                                }
                                bookingDeferred.resolve(booking);
                            });
                            promises.push(bookingDeferred.promise);
                        });

                        $q.all(promises).then(function (results) {
                            deferred.resolve(results);
                        });
                    });

                    return deferred.promise;
                };

                bookingsService.getBookingDetail = function (uuid) {
                    var deferred = $q.defer();
                    var self = this;

                    Bookings.get({uuid: uuid}).$promise.then(function (value) {
                        self.parseBookingDetail(value, function (booking) {
                            deferred.resolve(booking);
                        });
                    });

                    return deferred.promise;
                };

                bookingsService.parseBookingDetail = function (bookingData, parsedCallback) {
                    var bookingPromises = {};
                    var booking = {
                        total_amount: bookingData.total_amount,
                        deposit_amount: bookingData.deposit_amount,
                        start_date: UtilsService.formatDate(bookingData.started_at, "EEEE dd MMMM yyyy"),
                        end_date: UtilsService.formatDate(bookingData.ended_at, "EEEE dd MMMM yyyy"),
                        start_time: UtilsService.formatDate(bookingData.started_at, "HH'h'mm"),
                        end_time: UtilsService.formatDate(bookingData.ended_at, "HH'h'mm")
                    };

                    // Set period
                    var hourTime = 60 * 60 * 1000;
                    var dayTime = 24 * hourTime;

                    var startTime = Date.parse(bookingData.started_at);
                    var endTime = Date.parse(bookingData.ended_at);

                    var diffTime = endTime - startTime;

                    booking.period_days = Math.round(diffTime / dayTime);
                    booking.period_hours = Math.round((diffTime - dayTime * booking.period_days) / hourTime);

                    // Get product id
                    var productId = UtilsService.getIdFromUrl(bookingData.product);

                    // Get product
                    var productDeferred = $q.defer();
                    ProductsService.getProduct(productId).$promise.then(function (product) {
                        booking.title = product.summary;

                        var productPromises = {};

                        // Get address
                        var addressId = UtilsService.getIdFromUrl(product.address);
                        productPromises.address = AddressesService.getAddress(addressId).$promise;

                        // Get owner
                        var ownerId = UtilsService.getIdFromUrl(product.owner);
                        productPromises.owner = UsersService.get(ownerId).$promise;

                        // Get phone
                        var phoneId = UtilsService.getIdFromUrl(product.phone);
                        productPromises.phone = PhoneNumbersService.getPhoneNumber(phoneId).$promise;

                        $q.all(productPromises).then(function (results) {
                            var address = results.address;
                            booking.address = {};
                            booking.address.street = address.street;
                            booking.address.zipcode = address.zipcode;
                            booking.address.city = address.city;

                            var owner = results.owner;
                            booking.owner = {};
                            booking.owner.username = owner.username;
                            booking.owner.avatar = owner.avatar.thumbnail;

                            var phone = results.phone;
                            booking.owner.phone = phone.number;

                            productDeferred.resolve(booking);
                        });
                    });
                    bookingPromises.product = productDeferred.promise;

                    // Get picture
                    bookingPromises.pictures = PicturesService.getPicturesByProduct(productId).$promise;

                    $q.all(bookingPromises).then(function (results) {
                        if (jQuery(results.pictures.results).size() > 0) {
                            booking.picture = results.pictures.results[0].image.thumbnail;
                        }

                        parsedCallback(booking);
                    });
                };

                return bookingsService;
            }
        ]);

        /**
         * Service for managing pictures.
         */
        EloueCommon.factory("PicturesService", ["Pictures", function (Pictures) {
            var picturesService = {};

            picturesService.getPicturesByProduct = function (productId) {
                return Pictures.get({product: productId});
            };

            return picturesService;
        }]);

        /**
         * Service for managing addresses.
         */
        EloueCommon.factory("AddressesService", ["Addresses", function (Addresses) {
            var addressesService = {};

            addressesService.getAddress = function (addressId) {
                return Addresses.get({id: addressId});
            };

            return addressesService;
        }]);

        /**
         * Service for managing phone numbers.
         */
        EloueCommon.factory("PhoneNumbersService", ["PhoneNumbers", function (PhoneNumbers) {
            var phoneNumbersService = {};

            phoneNumbersService.getPhoneNumber = function (phoneNumbersId) {
                return PhoneNumbers.get({id: phoneNumbersId});
            };

            return phoneNumbersService;
        }]);
    });