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
        EloueCommon.factory("UsersService", ["Users", "FormService", "Endpoints",
            function (Users, FormService, Endpoints) {
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
            "ProductRelatedMessagesService",
            "UsersService",
            "ProductsService",
            "UtilsService",
            function ($q, $filter, MessageThreads, ProductRelatedMessagesService, UsersService, ProductsService,
                      UtilsService) {
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
                                    result.date = UtilsService.formatMessageDate(threadResults.lastMessage.sent_at,
                                        "HH'h'mm", "dd.mm.yyyy HH'h'mm");
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
                    var self = this;
                    var deferred = $q.defer();

                    // Send a request for a thread
                    MessageThreads.get({id: threadId, _cache: new Date().getTime()}).$promise.then(function (thread) {
                        var rootPromises = {};

                        // Get message list
                        var messagePromises = [];
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

                            messagePromises.push(messageDeferred.promise);
                        });
                        rootPromises.messages = $q.all(messagePromises);

                        // Get product
                        if (!!thread.product) {
                            var productDeferred = $q.defer();

                            var productId = self.getIdFromUrl(thread.product);
                            ProductsService.getProduct(productId).$promise.then(function (product) {
                                // TODO load rest of the fields
                                productDeferred.resolve(product);
                            });

                            rootPromises.product = productDeferred.promise;
                        }

                        $q.all(rootPromises).then(function (results) {
                            deferred.resolve(results);
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
            "UtilsService",
            function ($q, Bookings, ProductsService, PicturesService, UtilsService) {
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

                    Bookings.get({uuid: uuid}).$promise.then(function (value) {
                        var bookingPromises = {};

                        // Get product id
                        var productId = UtilsService.getIdFromUrl(value.product);

                        // Get product
                        bookingPromises.product = ProductsService.getProduct(productId).$promise;

                        // Get picture
                        bookingPromises.pictures = PicturesService.getPicturesByProduct(productId).$promise;

                        $q.all(bookingPromises).then(function (results) {
                            var booking = {};

                            booking.title = results.product.summary;
                            if (jQuery(results.pictures.results).size() > 0) {
                                booking.picture = results.pictures.results[0].image.thumbnail;
                            }
                            deferred.resolve(booking);
                        });
                    });

                    return deferred.promise;
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
    });