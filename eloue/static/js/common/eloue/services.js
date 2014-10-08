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

                usersService.getStatistics = function (userId) {
                    return Users.getStats({id: userId, _cache: new Date().getTime()});
                };

                usersService.sendForm = function (userId, form, successCallback, errorCallback) {
                    // Calculate current user url
                    var currentUserUrl = Endpoints.api_url + "users/" + userId + "/";

                    // Send form to the current user url
                    FormService.send("POST", currentUserUrl, form, successCallback, errorCallback);
                };

                usersService.resetPassword = function (userId, form) {
                    var resetPasswordUrl = Endpoints.api_url + "users/" + userId + "/reset_password/";
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

                usersService.updateUser = function (user) {
                    return Users.update({id: "me"}, user);
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
            "ProductRelatedMessages",
            "ProductRelatedMessagesService",
            "UsersService",
            "ProductsService",
            "BookingsService",
            "UtilsService",
            function ($q, $filter, MessageThreads, Bookings, ProductRelatedMessages, ProductRelatedMessagesService, UsersService, ProductsService, BookingsService, UtilsService) {
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
                                var messageId = UtilsService.getIdFromUrl(value.last_message);
                                threadPromises.lastMessage = ProductRelatedMessagesService.getMessage(messageId).$promise;
                            }

                            // Get sender
                            // TODO probably the field needs to be changed
                            var senderId = UtilsService.getIdFromUrl(value.sender);
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

                        // If product exists
                        if (!!thread.product) {
                            var productDeferred = $q.defer();
                            var ownerDeferred = $q.defer();

                            var productId = UtilsService.getIdFromUrl(thread.product);

                            // Get product
                            BookingsService.getBookingDetailProduct(productId).then(
                                function (product) {
                                    UsersService.get(product.ownerId).$promise.then(
                                        function (owner) {
                                            ownerDeferred.resolve(owner);
                                        },
                                        function (reason) {
                                            ownerDeferred.reject(reason);
                                        }
                                    );
                                    productDeferred.resolve(product);
                                },
                                function (reason) {
                                    productDeferred.reject(reason);
                                }
                            );
                            rootPromises.product = productDeferred.promise;
                            rootPromises.owner = ownerDeferred.promise;

                            /*Bookings.get({product: productId}).$promise.then(function (data) {
                             if ($.isArray(data.results) && (data.results.length > 0)) {
                             // If booking exists
                             var bookingData = data.results[data.results.length - 1];
                             BookingsService.parseBookingDetail(bookingData, function (booking) {
                             productDeferred.resolve(booking);
                             });
                             productDeferred.resolve("Booking");
                             } else {
                             // If no booking
                             // TODO no booking
                             productDeferred.resolve();
                             }
                             });*/
                        }

                        $q.all(rootPromises).then(function (results) {
                            var result = {
                                users: [],
                                messages: results.messages,
                                product: results.product,
                                owner: results.owner
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
                            var messageId = UtilsService.getIdFromUrl(value);
                            ProductRelatedMessagesService.getMessage(messageId).$promise.then(function (data) {
                                var result = {
                                    id: data.id,
                                    body: data.body,
                                    date: UtilsService.formatMessageDate(data.sent_at,
                                        "HH'h'mm", "dd.mm.yyyy HH'h'mm")
                                };

                                // Get sender
                                var senderId = UtilsService.getIdFromUrl(data.sender);
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
                            result.users.push(UtilsService.getIdFromUrl(thread.sender));
                            if (!!thread.recipient) {
                                result.users.push(UtilsService.getIdFromUrl(thread.recipient));
                            }

                            deferred.resolve(result);
                        });
                    });

                    return deferred.promise;
                };

                messageThreadsService.getMessageThread = function (productId, participantId) {
                    var deferred = $q.defer();
                    var self = this;
                    MessageThreads.list({product: productId, participant: participantId}).$promise.then(function (result) {
                        var promises = [];
                        angular.forEach(result.results, function (value, key) {
                            angular.forEach(value.messages, function (messageLink, idx) {
                                var messageId = UtilsService.getIdFromUrl(messageLink);
                                promises.push(ProductRelatedMessagesService.getMessage(messageId).$promise);
                            });
                        });
                        $q.all(promises).then(function success(results) {
                            deferred.resolve(results);
                        });
                    });
                    return deferred.promise;
                };

                messageThreadsService.sendMessage = function (message, productId) {
                    var threadDef = $q.defer();
                    var self = this;
                    if (!message.thread) {
                        var messageThread = {
                            "sender": message.sender,
                            "recipient": message.recipient,
                            "product": Endpoints.api_url + "products/" + productId + "/",
                            "subject": "Question",
                            "messages": []
                        };
                        MessageThreads.save({}, messageThread, function (response) {
                            threadDef.resolve(Endpoints.api_url + "messagethreads/" + response.id + "/");
                        });
                    } else {
                        threadDef.resolve(message.thread);
                    }
                    var deferred = $q.defer();
                    threadDef.promise.then(function (result) {
                        message.thread = result;
                        ProductRelatedMessages.save({}, message, function (response) {
                            var senderId = UtilsService.getIdFromUrl(response.sender);
                            UsersService.get(senderId).$promise.then(function (result) {
                                response.sender = result;
                                deferred.resolve(response);
                            });
                        });
                    });
                    return deferred.promise;
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
        EloueCommon.factory("ProductsService", [
            "$q",
            "$timeout",
            "AddressesService",
            "Bookings",
            "Products",
            "CategoriesService",
            "PhoneNumbersService",
            "PicturesService",
            "PricesService",
            "UtilsService",
            "UsersService",
            "MessageThreads",
            function ($q, $timeout, AddressesService, Bookings, Products, CategoriesService, PhoneNumbersService, PicturesService, PricesService, UtilsService, UsersService, MessageThreads) {
                var productsService = {};

                productsService.getProduct = function (id) {
                    return Products.get({id: id});
                };

                productsService.getProductDetails = function (id) {
                    var deferred = $q.defer();
                    var self = this;
                    Products.get({id: id}).$promise.then(function (result) {
                        var promises = [];
                        promises.push(PicturesService.getPicturesByProduct(id).$promise);
                        var categoryId = UtilsService.getIdFromUrl(result.category);
                        promises.push(CategoriesService.getCategory(categoryId).$promise);
                        var ownerId = UtilsService.getIdFromUrl(result.owner);
                        promises.push(UsersService.get(ownerId).$promise);
                        $q.all(promises).then(function success(results) {
                            result.pictures = results[0].results;
                            result.categoryDetails = results[1];
                            result.ownerDetails = results[2];
                            deferred.resolve(result);
                        });
                    });
                    return deferred.promise;
                };

                productsService.getProductsByAddress = function (addressId) {
                    var deferred = $q.defer();

                    Products.get({address: addressId}).$promise.then(function (data) {
                        var promises = [];

                        angular.forEach(data.results, function (value, key) {
                            var productDeferred = $q.defer();

                            var product = {
                                id: value.id,
                                summary: value.summary,
                                deposit_amount: value.deposit_amount
                            };

                            PicturesService.getPicturesByProduct(value.id).$promise.then(
                                function (pictures) {
                                    if ($.isArray(pictures.results) && (pictures.results.length > 0)) {
                                        product.picture = pictures.results[0].image.thumbnail;
                                    }
                                    productDeferred.resolve(product);
                                },
                                function (reason) {
                                    productDeferred.reject(reason);
                                }
                            );

                            promises.push(productDeferred.promise);
                        });

                        $q.all(promises).then(
                            function (results) {
                                deferred.resolve(results);
                            },
                            function (reasons) {
                                deferred.reject(reasons);
                            }
                        );
                    });

                    return deferred.promise;
                };

                productsService.getProductsByOwnerAndRootCategory = function (userId, rootCategoryId, page) {
                    var deferred = $q.defer();
                    var params = {owner: userId};

                    if (rootCategoryId) {
                        params.category__isdescendant = rootCategoryId;
                    }

                    if (page) {
                        params.page = page;
                    }

                    Products.get(params).$promise.then(function (data) {
                        var promises = [];
                        angular.forEach(data.results, function (value, key) {
                            var productDeferred = $q.defer();

                            var product = {
                                id: value.id,
                                summary: value.summary,
                                deposit_amount: value.deposit_amount
                            };

                            var subPromises = [];

                            subPromises.push(PicturesService.getPicturesByProduct(product.id).$promise);
                            subPromises.push(PricesService.getProductPricesPerDay(product.id).$promise);
                            subPromises.push(Products.getStats({id: product.id}).$promise);
                            $q.all(subPromises).then(
                                function (results) {

                                    var pictures = results[0];
                                    if ($.isArray(pictures.results) && (pictures.results.length > 0)) {
                                        product.picture = pictures.results[0].image.thumbnail;
                                    }

                                    var prices = results[1];
                                    if (prices.results && prices.results.length > 0) {
                                        product.pricePerDay = prices.results[0].amount;
                                    } else {
                                        product.pricePerDay = 0;
                                    }

                                    product.stats = results[2];
                                    productDeferred.resolve(product);
                                },
                                function (reasons) {
                                    productDeferred.reject(reasons);
                                }
                            );

                            promises.push(productDeferred.promise);
                        });

                        $q.all(promises).then(
                            function (results) {
                                deferred.resolve({
                                    list: results,
                                    next: data.next
                                });
                            },
                            function (reasons) {
                                deferred.reject(reasons);
                            }
                        );
                    });

                    return deferred.promise;
                };

                productsService.saveProduct = function (product) {
                    return Products.save(product);
                };

                productsService.updateProduct = function (product) {
                    return Products.update({id: product.id}, product);
                };

                return productsService;
            }
        ]);

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
                return this.formatDate(sentDate, dateFormat);
            };

            utilsService.getIdFromUrl = function (url) {
                var trimmedUrl = url.slice(0, url.length - 1);
                return trimmedUrl.substring(trimmedUrl.lastIndexOf("/") + 1, url.length);
            };

            utilsService.calculatePeriodBetweenDates = function (startDateString, endDateString) {
                var hourTime = 60 * 60 * 1000;
                var dayTime = 24 * hourTime;

                var startTime = Date.parse(startDateString).getTime();
                var endTime = Date.parse(endDateString).getTime();

                var diffTime = endTime - startTime;

                var periodDays = Math.floor(diffTime / dayTime);
                var periodHours = Math.floor((diffTime - dayTime * periodDays) / hourTime);

                return {
                    period_days: periodDays,
                    period_hours: periodHours
                };
            };

            return utilsService;
        }]);

        /**
         * Service for managing bookings.
         */
        EloueCommon.factory("BookingsService", [
            "$q",
            "Bookings",
            "Products",
            "ProductsService",
            "PicturesService",
            "AddressesService",
            "UsersService",
            "PhoneNumbersService",
            "CommentsService",
            "UtilsService",
            function ($q, Bookings, Products, ProductsService, PicturesService, AddressesService, UsersService, PhoneNumbersService, CommentsService, UtilsService) {
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

                bookingsService.getBookingsByProduct = function (productId) {
                    var deferred = $q.defer();

                    Bookings.get({product: productId}).$promise.then(function (data) {
                        var promises = [];

                        angular.forEach(data.results, function (value, key) {
                            var bookingDeferred = $q.defer();
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

                            var bookingPromises = {};

                            // Get product id
                            var productId = UtilsService.getIdFromUrl(value.product);

                            // Get product
                            bookingPromises.product = ProductsService.getProduct(productId).$promise;

                            var borrowerId = UtilsService.getIdFromUrl(value.borrower);
                            bookingPromises.borrower = UsersService.get(borrowerId).$promise;

                            // Get picture
                            bookingPromises.pictures = PicturesService.getPicturesByProduct(productId).$promise;

                            $q.all(bookingPromises).then(function (results) {
                                booking.title = results.product.summary;
                                if (jQuery(results.pictures.results).size() > 0) {
                                    booking.picture = results.pictures.results[0].image.thumbnail;
                                }
                                booking.borrower = results.borrower;
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

                bookingsService.getBooking = function (uuid) {
                    var deferred = $q.defer();

                    Bookings.get({uuid: uuid}).$promise.then(
                        function (booking) {
                            var resultBooking = {
                                total_amount: booking.total_amount,
                                deposit_amount: booking.deposit_amount,
                                start_date: {
                                    week_day: UtilsService.formatDate(booking.started_at, "EEEE"),
                                    day: UtilsService.formatDate(booking.started_at, "dd"),
                                    month: UtilsService.formatDate(booking.started_at, "MMMM"),
                                    year: UtilsService.formatDate(booking.started_at, "yyyy")
                                },
                                end_date: {
                                    week_day: UtilsService.formatDate(booking.ended_at, "EEEE"),
                                    day: UtilsService.formatDate(booking.ended_at, "dd"),
                                    month: UtilsService.formatDate(booking.ended_at, "MMMM"),
                                    year: UtilsService.formatDate(booking.ended_at, "yyyy")
                                },
                                start_time: UtilsService.formatDate(booking.started_at, "HH'h'mm"),
                                end_time: UtilsService.formatDate(booking.ended_at, "HH'h'mm")
                            };

                            // Set period
                            var period = UtilsService.calculatePeriodBetweenDates(booking.started_at, booking.ended_at);

                            resultBooking.period_days = period.period_days;
                            resultBooking.period_hours = period.period_hours;

                            // Set product id
                            resultBooking.productId = UtilsService.getIdFromUrl(booking.product);

                            // Get owner and borrower
                            var promises = {};
                            // Get owner
                            var ownerId = UtilsService.getIdFromUrl(booking.owner);
                            promises.owner = UsersService.get(ownerId).$promise;

                            // Get borrower
                            var borrowerId = UtilsService.getIdFromUrl(booking.borrower);
                            promises.borrower = UsersService.get(borrowerId).$promise;

                            $q.all(promises).then(
                                function (data) {
                                    resultBooking.owner = data.owner;
                                    resultBooking.borrower = data.borrower;
                                    deferred.resolve(resultBooking);
                                },
                                function (reason) {
                                    deferred.reject(reason);
                                }
                            );
                        },
                        function (reason) {
                            deferred.reject(reason);
                        }
                    );

                    return deferred.promise;
                };

                bookingsService.getBookingDetailProduct = function (productId) {
                    var productDeferred = $q.defer();

                    Products.get({id: productId}).$promise.then(
                        function (product) {
                            var resultProduct = {
                                summary: product.summary
                            };

                            var productPromises = {};

                            // Get picture
                            productPromises.pictures = PicturesService.getPicturesByProduct(productId).$promise;

                            // Get owner id
                            resultProduct.ownerId = UtilsService.getIdFromUrl(product.owner);

                            $q.all(productPromises).then(
                                function (results) {

                                    // Set picture
                                    if ($.isArray(results.pictures.results) && $(results.pictures.results).size() > 0) {
                                        resultProduct.picture = results.pictures.results[0].image.thumbnail;
                                    }

                                    productDeferred.resolve(resultProduct);
                                },
                                function (reason) {
                                    productDeferred.reject(reason);
                                }
                            );
                        },
                        function (reason) {
                            productDeferred.reject(reason);
                        });

                    return productDeferred.promise;
                };

                bookingsService.getBookingDetailInformation = function (uuid) {
                    var deferred = $q.defer();
                    var self = this;

                    self.getBooking(uuid).then(
                        function (booking) {
                            var bookingDetail = {
                                booking: booking
                            };

                            var promises = {};

                            // Get product
                            var productDeferred = $q.defer();
                            self.getBookingDetailProduct(booking.productId).then(
                                function (product) {
                                    bookingDetail.product = product;
                                    bookingDetail.phone = product.phone;
                                    productDeferred.resolve(bookingDetail);
                                },
                                function (reason) {
                                    productDeferred.reject(reason);
                                }
                            );
                            promises.product = productDeferred.promise;

                            // Get comments
                            var commentsDeferred = $q.defer();

                            CommentsService.getCommentList(uuid).then(
                                function (comments) {
                                    var commentList = comments.results;

                                    angular.forEach(commentList, function (value, key) {
                                        value.author = (value.type == 0) ? booking.owner : booking.borrower
                                    });

                                    bookingDetail.comments = commentList;
                                    commentsDeferred.resolve(bookingDetail);
                                },
                                function (reason) {
                                    commentsDeferred.reject(reason);
                                }
                            );

                            promises.comments = commentsDeferred.promise;

                            $q.all(promises).then(
                                function () {
                                    deferred.resolve(bookingDetail);
                                },
                                function (reasons) {
                                    deferred.reject(reasons);
                                }
                            );
                        },
                        function (reason) {
                            deferred.reject(reason);
                        }
                    );

                    return deferred.promise;
                };

                return bookingsService;
            }
        ]);

        /**
         * Service for managing categories.
         */
        EloueCommon.factory("CategoriesService", ["$q", "Categories", "UtilsService", function ($q, Categories, UtilsService) {
            var categoriesService = {};

            categoriesService.getCategory = function (categoryId) {
                return Categories.get({id: categoryId});
            };

            categoriesService.getCategoryByName = function (categoryName) {
                return Categories.get({name: categoryName});
            };

            categoriesService.getParentCategory = function (category) {
                var parentCategoryId = UtilsService.getIdFromUrl(category.parent);
                return categoriesService.getCategory(parentCategoryId);
            };

            categoriesService.searchByProductTitle = function (query, rootCategoryId) {
                var deferred = $q.defer();

                $.ajax({
                    url: "/location/ajouter/category/?q=" + query + "&category=" + rootCategoryId,
                    type: "GET",
                    success: function(data) {
                        deferred.resolve(data.categories);
                    }
                });

                return deferred.promise;
            };

            categoriesService.getRootCategories = function () {
                var deferred = $q.defer();

                Categories.get({parent__isnull: true}).$promise.then(function (result) {
                    var total = result.count;
                    if (total <= 10) {
                        deferred.resolve(result.results);
                    } else {
                        var pagesCount = Math.floor(total / 10) + 1;
                        var catPromises = [];

                        for (var i = 1; i <= pagesCount; i++) {
                            catPromises.push(Categories.get({parent__isnull: true, page: i}).$promise);
                        }

                        $q.all(catPromises).then(
                            function (categories) {
                                var categoryList = [];
                                angular.forEach(categories, function (catPage, index) {
                                    angular.forEach(catPage.results, function (value, key) {
                                        categoryList.push({id: value.id, name: value.name})
                                    });
                                });
                                deferred.resolve(categoryList);
                            }
                        );

                    }
                });

                return deferred.promise;
            };

            categoriesService.getChildCategories = function (parentId) {
                var deferred = $q.defer();
                Categories.getChildren({id: parentId}).$promise.then(function (categories) {
                    var categoryList = [];
                    angular.forEach(categories, function (value, key) {
                        categoryList.push({id: value.id, name: value.name});
                    });
                    deferred.resolve(categoryList);
                });
                return deferred.promise;
            };

            return categoriesService;
        }]);

        /**
         * Service for managing prices.
         */
        EloueCommon.factory("PricesService", ["Prices", function (Prices) {
            var pricesService = {};

            pricesService.getProductPricesPerDay = function (productId) {
                return Prices.getProductPricesPerDay({product: productId});
            };

            pricesService.getPricesByProduct = function (productId) {
                return Prices.get({product: productId});
            };

            pricesService.savePrice = function (price) {
                return Prices.save(price);
            };

            pricesService.updatePrice = function (price) {
                return Prices.update({id: price.id}, price);
            };

            return pricesService;
        }]);

        /**
         * Service for managing pictures.
         */
        EloueCommon.factory("PicturesService", ["Pictures", "Endpoints", "FormService", function (Pictures, Endpoints, FormService) {
            var picturesService = {};

            picturesService.getPicturesByProduct = function (productId) {
                return Pictures.get({product: productId});
            };

            picturesService.savePicture = function (productId, form, successCallback, errorCallback) {
                // Calculate current user url
                var url = Endpoints.api_url + "pictures/";

                // Send form to the url
                FormService.send("POST", url, form, successCallback, errorCallback);
            };

            return picturesService;
        }]);

        /**
         * Service for managing addresses.
         */
        EloueCommon.factory("AddressesService", [
            "$q",
            "Addresses",
            "Endpoints",
            "FormService",
            function ($q, Addresses, Endpoints, FormService) {
                var addressesService = {};

                addressesService.getAddress = function (addressId) {
                    return Addresses.get({id: addressId});
                };

                addressesService.getAddressesByPatron = function (patronId) {
                    return Addresses.get({patron: patronId});
                };

                addressesService.updateAddress = function (addressId, formData) {
                    var deferred = $q.defer();

                    var currentAddressUrl = Endpoints.api_url + "addresses/" + addressId + "/";
                    FormService.send("POST", currentAddressUrl, formData,
                        function (data) {
                            deferred.resolve(data);
                        },
                        function (reason) {
                            deferred.reject(reason);
                        });

                    return deferred.promise;
                };

                //TODO: leave only 1 update method for addresses
                addressesService.update = function (address) {
                    return Addresses.update({id: address.id}, address);
                };

                addressesService.saveAddress = function (address) {
                    return Addresses.save(address);
                };

                addressesService.deleteAddress = function (addressId) {
                    return Addresses.delete({id: addressId});
                };

                return addressesService;
            }
        ]);

        /**
         * Service for managing phone numbers.
         */
        EloueCommon.factory("PhoneNumbersService", ["PhoneNumbers", function (PhoneNumbers) {
            var phoneNumbersService = {};

            phoneNumbersService.getPhoneNumber = function (phoneNumberId) {
                return PhoneNumbers.get({id: phoneNumberId});
            };

            phoneNumbersService.updatePhoneNumber = function (phoneNumber) {
                return PhoneNumbers.update({id: phoneNumber.id}, phoneNumber);
            };

            phoneNumbersService.getPremiumRateNumber = function (phoneNumberId) {
                return PhoneNumbers.getPremiumRateNumber({id: phoneNumberId});
            };

            return phoneNumbersService;
        }]);

        /**
         * Service for managing comments.
         */
        EloueCommon.factory("CommentsService", [
            "Comments",
            "Endpoints",
            function (Comments, Endpoints) {
                var commentsService = {};

                commentsService.getCommentList = function (bookingUUID) {
                    return Comments.get({_cache: new Date().getTime(), booking: bookingUUID}).$promise;
                };

                commentsService.postComment = function (bookingUUID, comment, rate) {
                    var bookingUrl = Endpoints.api_url + "bookings/" + bookingUUID + "/";
                    return Comments.save({
                        booking: bookingUrl,
                        comment: comment,
                        rate: rate
                    });
                };

                return commentsService;
            }
        ]);

        /**
         * Service for managing comments.
         */
        EloueCommon.factory("CreditCardsService", [
            "CreditCards",
            "Endpoints",
            function (CreditCards, Endpoints) {
                var creditCardsService = {};

                creditCardsService.getCardsByHolder = function (holderId) {
                    return CreditCards.get({holder: holderId, _cache: new Date().getTime()}).$promise;
                };

                creditCardsService.saveCard = function (card) {
                    return CreditCards.save(card);
                };

                creditCardsService.updateCard = function (card) {
                    return CreditCards.update({id: card.id}, card);
                };

                creditCardsService.deleteCard = function (card) {
                    return CreditCards.delete({id: card.id});
                };

                return creditCardsService;
            }
        ]);

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

        /**
         * Service for parsing products.
         */
        EloueCommon.factory("ProductsParseService", [function () {
            var productsParseService = {};

            productsParseService.parseProduct = function (productData, statsData, ownerData, ownerStatsData, picturesDataArray) {
                var productResult = angular.copy(productData);

                productResult.stats = statsData;

                // Parse owner
                if (!!ownerData) {
                    productResult.owner = ownerData;
                }

                if (!!ownerStatsData) {
                    productResult.ownerStats = ownerStatsData;
                }

                // Parse pictures
                if (angular.isArray(picturesDataArray) && picturesDataArray.length > 0) {
                    productResult.picture = picturesDataArray[0].image.thumbnail;
                }

                return productResult;
            };

            return productsParseService;
        }]);

        /**
         * Service for parsing comments.
         */
        EloueCommon.factory("CommentsParseService", [function () {
            var commentsParseService = {};

            commentsParseService.parseComment = function (commentData, authorData) {
                var commentResult = angular.copy(commentData);

                // Parse author
                if (!!authorData) {
                    commentResult.author = authorData;
                }

                return commentResult;
            };

            return commentsParseService;
        }]);

        /**
         * Service for managing bookings.
         */
        EloueCommon.factory("BookingsLoadService", [
            "$q",
            "Bookings",
            "PicturesService",
            "UtilsService",
            "BookingsParseService",
            "ProductsLoadService",
            "MessageThreadsService",
            function ($q, Bookings, PicturesService, UtilsService, BookingsParseService, ProductsLoadService, MessageThreadsService) {
                var bookingsLoadService = {};

                bookingsLoadService.getBookingList = function (author, page) {
                    var deferred = $q.defer();

                    // Load bookings
                    Bookings.get({page: page, author: author, _cache: new Date().getTime()}).$promise.then(function (bookingListData) {
                        var bookingListPromises = [];

                        // For each booking
                        angular.forEach(bookingListData.results, function (bookingData, key) {
                            var bookingDeferred = $q.defer();
                            var bookingPromises = {};

                            // Get product id
                            var productId = UtilsService.getIdFromUrl(bookingData.product);

                            // Load product
                            bookingPromises.product = ProductsLoadService.getProduct(productId);

                            // Load pictures
                            bookingPromises.pictures = PicturesService.getPicturesByProduct(productId).$promise;

                            // When all data loaded
                            $q.all(bookingPromises).then(function (bookingResults) {
                                var booking = BookingsParseService.parseBookingListItem(bookingData, bookingResults.product, bookingResults.pictures.results);
                                bookingDeferred.resolve(booking);
                            });

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
                    Bookings.get({uuid: bookingUUID, _cache: new Date().getTime()}).$promise.then(function (bookingData) {
                        var booking = BookingsParseService.parseBooking(bookingData);
                        deferred.resolve(booking);
                    });

                    return deferred.promise;
                };

                bookingsLoadService.getBookingDetails = function (bookingUUID) {
                    var deferred = $q.defer();

                    // Load booking
                    this.getBooking(bookingUUID).then(function (booking) {
                        // Get product id
                        var productId = UtilsService.getIdFromUrl(booking.product);
                        // Load product
                        ProductsLoadService.getProduct(productId, true, true).then(function (product) {
                            booking.product = product;
                            MessageThreadsService.getMessageThread(product.id, UtilsService.getIdFromUrl(booking.borrower)).then(function(threads) {
                                if (threads && threads.length > 0) {
                                    booking.lastThreadId = UtilsService.getIdFromUrl(threads[threads.length - 1].thread);
                                }
                                deferred.resolve(booking);
                            });

                        });
                    });

                    return deferred.promise;
                };

                bookingsLoadService.getBookingByProduct = function (productId) {
                    var deferred = $q.defer();

                    // Load all bookings for this product
                    Bookings.get({product: productId, _cache: new Date().getTime()}).$promise.then(function (bookingListData) {
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

        /**
         * Service for managing products.
         */
        EloueCommon.factory("ProductsLoadService", [
            "$q",
            "Products",
            "CheckAvailability",
            "AddressesService",
            "UsersService",
            "PicturesService",
            "PhoneNumbersService",
            "UtilsService",
            "ProductsParseService",
            function ($q, Products, CheckAvailability, AddressesService, UsersService, PicturesService, PhoneNumbersService, UtilsService, ProductsParseService) {
                var productLoadService = {};

                productLoadService.getProduct = function (productId, loadOwner, loadPictures) {
                    var deferred = $q.defer();

                    // Load product
                    Products.get({id: productId, _cache: new Date().getTime()}).$promise.then(function (productData) {
                        var productPromises = {};

                        productPromises.stats = Products.getStats({id: productId, _cache: new Date().getTime()});

                        if (loadOwner) {
                            // Get owner id
                            var ownerId = UtilsService.getIdFromUrl(productData.owner);
                            // Load owner
                            productPromises.owner = UsersService.get(ownerId).$promise;
                            productPromises.ownerStats = UsersService.getStatistics(ownerId).$promise;
                        }

                        if (loadPictures) {
                            // Load pictures
                            productPromises.pictures = PicturesService.getPicturesByProduct(productId).$promise;
                        }

                        // When all data loaded
                        $q.all(productPromises).then(function (results) {
                            var product = ProductsParseService.parseProduct(productData, results.stats, results.owner,
                                results.ownerStats, (!!results.pictures) ? results.pictures.results : null);
                            deferred.resolve(product);
                        });
                    });

                    return deferred.promise;
                };

                productLoadService.isAvailable = function (id, startDate, endDate, quantity) {
                    return CheckAvailability.get({id: id, started_at: startDate, ended_at: endDate, quantity: quantity}).$promise;
                };

                return productLoadService;
            }
        ]);

        /**
         * Service for managing comments.
         */
        EloueCommon.factory("CommentsLoadService", [
            "$q",
            "Comments",
            "Endpoints",
            "UsersService",
            "UtilsService",
            "CommentsParseService",
            function ($q, Comments, Endpoints, UsersService, UtilsService, CommentsParseService) {
                var commentsLoadService = {};

                commentsLoadService.getCommentList = function (bookingUUID) {
                    var deferred = $q.defer();
                    var commentListPromises = [];

                    // Load comments
                    Comments.get({booking: bookingUUID, _cache: new Date().getTime()}).$promise.then(function (commentListData) {
                        angular.forEach(commentListData.results, function (commentData, key) {
                            var commentDeferred = $q.defer();

                            // Get author id
                            var authorId = UtilsService.getIdFromUrl(commentData.author);
                            // Load author
                            UsersService.get(authorId).$promise.then(function (authorData) {
                                var comment = CommentsParseService.parseComment(commentData, authorData);
                                commentDeferred.resolve(comment);
                            });

                            commentListPromises.push(commentDeferred.promise);
                        });

                        $q.all(commentListPromises).then(function (results) {
                            deferred.resolve(results);
                        });
                    });

                    return deferred.promise;
                };

                commentsLoadService.postComment = function (bookingUUID, comment, rate) {
                    var bookingUrl = Endpoints.api_url + "bookings/" + bookingUUID + "/";
                    return Comments.save({
                        booking: bookingUrl,
                        comment: comment,
                        rate: rate
                    });
                };

                return commentsLoadService;
            }
        ]);

        /**
         * Service for managing message threads.
         */
        EloueCommon.factory("MessageThreadsLoadService", [
            "$q",
            "MessageThreads",
            "UsersService",
            "ProductRelatedMessagesService",
            "UtilsService",
            "MessageThreadsParseService",
            "ProductRelatedMessagesLoadService",
            "ProductsLoadService",
            function ($q, MessageThreads, UsersService, ProductRelatedMessagesService, UtilsService, MessageThreadsParseService, ProductRelatedMessagesLoadService, ProductsLoadService) {
                var messageThreadsLoadService = {};

                messageThreadsLoadService.getMessageThreadList = function (loadSender, loadLastMessage, page) {
                    var deferred = $q.defer();

                    // Load message threads
                    MessageThreads.get({page: page, _cache: new Date().getTime()}).$promise.then(function (messageThreadListData) {
                        var messageThreadListPromises = [];

                        // For each message thread
                        angular.forEach(messageThreadListData.results, function (messageThreadData, key) {
                            var messageThreadDeferred = $q.defer();
                            var messageThreadPromises = {};

                            // Get sender id
                            if (loadSender) {
                                var senderId = UtilsService.getIdFromUrl(messageThreadData.sender);
                                // Load sender
                                messageThreadPromises.sender = UsersService.get(senderId).$promise;
                            }

                            // Get last message id
                            if (loadLastMessage && !!messageThreadData.last_message) {
                                var lastMessageId = UtilsService.getIdFromUrl(messageThreadData.last_message);
                                // Load last message
                                messageThreadPromises.last_message = ProductRelatedMessagesService.getMessage(lastMessageId).$promise;
                            }

                            // When all data loaded
                            $q.all(messageThreadPromises).then(function (messageThreadResults) {
                                var messageThread = MessageThreadsParseService.parseMessageThreadListItem(messageThreadData,
                                    messageThreadResults.sender, messageThreadResults.last_message);
                                messageThreadDeferred.resolve(messageThread);
                            });

                            messageThreadListPromises.push(messageThreadDeferred.promise);
                        });

                        $q.all(messageThreadListPromises).then(function (messageThreadList) {
                            deferred.resolve({
                                list: messageThreadList,
                                next: messageThreadListData.next
                            });
                        });
                    });

                    return deferred.promise;
                };

                messageThreadsLoadService.getMessageThread = function (threadId) {
                    var deferred = $q.defer();

                    // Load message thread
                    MessageThreads.get({id: threadId, _cache: new Date().getTime()}).$promise.then(function (messageThreadData) {
                        var messageThreadPromises = {};

                        // Load messages
                        var messagesPromises = [];
                        angular.forEach(messageThreadData.messages, function (messageUrl, key) {
                            // Get message id
                            var messageId = UtilsService.getIdFromUrl(messageUrl);
                            // Load message
                            messagesPromises.push(ProductRelatedMessagesLoadService.getMessageListItem(messageId));
                        });
                        // When all messages loaded
                        messageThreadPromises.messages = $q.all(messagesPromises);

                        // Get product id
                        if (messageThreadData.product) {
                            var productId = UtilsService.getIdFromUrl(messageThreadData.product);
                            messageThreadPromises.product = ProductsLoadService.getProduct(productId, true, true);
                        }

                        $q.all(messageThreadPromises).then(function (results) {
                            var messageThread = MessageThreadsParseService.parseMessageThread(messageThreadData, results.messages, results.product);
                            deferred.resolve(messageThread);
                        });
                    });

                    return deferred.promise;
                };

                messageThreadsLoadService.getUsersRoles = function (messageThread, currentUserId) {
                    var senderId = UtilsService.getIdFromUrl(messageThread.sender);
                    var recipientId = UtilsService.getIdFromUrl(messageThread.recipient);

                    var result = {
                        senderId: currentUserId
                    };

                    if (senderId == currentUserId) {
                        result.recipientId = recipientId;
                    } else {
                        result.recipientId = senderId;
                    }

                    return result;
                };

                return messageThreadsLoadService;
            }
        ]);

        /**
         * Service for parsing message threads.
         */
        EloueCommon.factory("MessageThreadsParseService", [
            "UtilsService",
            function (UtilsService) {
                var messageThreadsParseService = {};

                messageThreadsParseService.parseMessageThreadListItem = function (messageThreadData, senderData, lastMessageData) {
                    var messageThreadResult = angular.copy(messageThreadData);

                    // Parse sender
                    if (!!senderData) {
                        messageThreadResult.sender = senderData;
                    }

                    // Parse last message
                    if (!!lastMessageData) {
                        messageThreadResult.last_message = lastMessageData;
                        messageThreadResult.last_message.sent_at = UtilsService.formatDate(lastMessageData.sent_at, "dd.mm.yyyy HH'h'mm");
                    }

                    return messageThreadResult;
                };

                messageThreadsParseService.parseMessageThread = function (messageThreadData, messagesDataArray, productData) {
                    var messageThreadResult = angular.copy(messageThreadData);

                    // Parse messages
                    if (!!messagesDataArray) {
                        messageThreadResult.messages = messagesDataArray;
                        angular.forEach(messageThreadResult.messages, function (message, key) {
                            message.sent_at = UtilsService.formatDate(message.sent_at, "dd.mm.yyyy HH'h'mm");
                        });
                    }

                    // Parse product
                    if (!!productData) {
                        messageThreadResult.product = productData;
                    }

                    return messageThreadResult;
                };
                return messageThreadsParseService;
            }
        ]);

        /**
         * Service for managing product related messages.
         */
        EloueCommon.factory("ProductRelatedMessagesLoadService", [
            "$q",
            "ProductRelatedMessages",
            "Endpoints",
            "MessageThreads",
            "UsersService",
            "UtilsService",
            "ProductRelatedMessagesParseService",
            function ($q, ProductRelatedMessages, Endpoints, MessageThreads, UsersService, UtilsService, ProductRelatedMessagesParseService) {
                var productRelatedMessagesLoadService = {};

                productRelatedMessagesLoadService.getMessage = function (messageId) {
                    return ProductRelatedMessages.get({id: messageId, _cache: new Date().getTime()}).$promise;
                };

                productRelatedMessagesLoadService.getMessageListItem = function (messageId) {
                    var deferred = $q.defer();

                    this.getMessage(messageId).then(function (messageData) {
                        // Get sender id
                        var senderId = UtilsService.getIdFromUrl(messageData.sender);
                        // Load sender
                        UsersService.get(senderId).$promise.then(function (senderData) {
                            var message = ProductRelatedMessagesParseService.parseMessage(messageData, senderData);
                            deferred.resolve(message);
                        });

                    });

                    return deferred.promise;
                };

                productRelatedMessagesLoadService.postMessage = function (threadId, senderId, recipientId, text, offerId, productId) {
                    var threadDef = $q.defer();
                    var self = this;
                    if (!threadId) {
                        var messageThread = {
                            sender: Endpoints.api_url + "users/" + senderId + "/",
                            recipient: Endpoints.api_url + "users/" + recipientId + "/",
                            product: Endpoints.api_url + "products/" + productId + "/",
                            subject: "Question",
                            messages: []
                        };
                        MessageThreads.save({}, messageThread, function (response) {
                            threadDef.resolve(response.id);
                        });
                    } else {
                        threadDef.resolve(threadId);
                    }
                    var deferred = $q.defer();
                    threadDef.promise.then(function (result) {
                        var message = {
                            thread: Endpoints.api_url + "messagethreads/" + result + "/",
                            sender: Endpoints.api_url + "users/" + senderId + "/",
                            recipient: Endpoints.api_url + "users/" + recipientId + "/",
                            body: (!!text) ? text : "",
                            offer: (!!offerId) ? Endpoints.api_url + "bookings/" + offerId + "/" : null
                        };
                        ProductRelatedMessages.save({}, message, function (response) {
                            var senderId = UtilsService.getIdFromUrl(response.sender);
                            UsersService.get(senderId).$promise.then(function (result) {
                                response.sender = result;
                                deferred.resolve(response);
                            });
                        });
                    });
                    return deferred.promise;
                };

                return productRelatedMessagesLoadService;
            }
        ]);

        /**
         * Service for parsing product related messages.
         */
        EloueCommon.factory("ProductRelatedMessagesParseService", [function () {
            var productRelatedMessagesParseService = {};

            productRelatedMessagesParseService.parseMessage = function (messageData, senderData) {
                var messageResults = angular.copy(messageData);

                // Parse sender
                if (!!senderData) {
                    messageResults.sender = senderData;
                }

                return messageResults;
            };

            return productRelatedMessagesParseService;
        }]);

        EloueCommon.factory("AuthService", ["$q", "$window", "Endpoints", "AuthConstants", "RedirectAfterLogin", "Registration", "FormService", function ($q, $window, Endpoints, AuthConstants, RedirectAfterLogin, Registration, FormService) {
            return {

                /**
                 * Sign in user with provided credentials.
                 * @param credentials user credentials
                 * @returns Signed in user object
                 * @param successCallback success callback function
                 * @param errorCallback error callback function
                 */
                login: function (credentials, successCallback, errorCallback) {
                    $.ajax({
                        url: Endpoints.oauth_url + "access_token/",
                        type: "POST",
                        data: {
                            client_id: AuthConstants.clientId,
                            client_secret: AuthConstants.clientSecret,
                            grant_type: AuthConstants.grantType,
                            username: credentials.username,
                            password: credentials.password
                        },
                        success: successCallback,
                        error: errorCallback
                    });
                },

                /**
                 * Remove user token.
                 */
                clearUserData: function () {
                    document.cookie = "user_token=;expires=" + new Date(0).toGMTString();
                },

                /**
                 * Redirect to attempted URL.
                 */
                redirectToAttemptedUrl: function () {
                    $window.location.href = RedirectAfterLogin.url;
                },

                /**
                 * Save URL that user attempts to access.
                 */
                saveAttemptUrl: function () {
                    RedirectAfterLogin.url = $window.location.href;
                },

                /**
                 * Sends password reset request.
                 * @param form form
                 * @param successCallback success callback
                 * @param errorCallback error callback
                 */
                sendResetPasswordRequest: function(form, successCallback, errorCallback) {
                    FormService.send("POST", "/reset/", form, successCallback, errorCallback);
                },

                /**
                 * Sends password reset request.
                 * @param form form
                 * @param url post url
                 * @param successCallback success callback
                 * @param errorCallback error callback
                 */
                resetPassword: function(form, url, successCallback, errorCallback) {
                    FormService.send("POST", url, form, successCallback, errorCallback);
                },

                /**
                 * Register new account
                 * @param account new account
                 * @returns user promise object.
                 */
                register: function (account) {
                    return Registration.register(account);
                },

                /**
                 * Check if app user is logged in.
                 * @returns true if user is logged in
                 */
                isLoggedIn: function () {
                    return !!this.getCookie("user_token");
                },

                /**
                 * Retrieves cookie value by provided cookie name.
                 * @param cname cookie name
                 */
                getCookie: function getCookie(cname) {
                    var name = cname + "=";
                    var ca = document.cookie.split(';');
                    for (var i = 0; i < ca.length; i++) {
                        var c = ca[i];
                        while (c.charAt(0) == ' ') c = c.substring(1);
                        if (c.indexOf(name) != -1) return c.substring(name.length, c.length);
                    }
                    return "";
                }
            };
        }]);

        EloueCommon.factory("LazyLoader", ["$timeout", "$rootScope", "$q", function ($timeout, $rootScope, $q) {
            var config,
                data,
                fetch,
                args;
            return {

                configure: function (options) {
                    config = options;
                    data = config.data;
                    fetch = config.fetchData;
                    args = config.args;
                },

                getData: function () {
                    var deferred = $q.defer();
                    $rootScope.$broadcast("showLoading");

                    fetch.apply(null, args).then(function (res) {
                        deferred.resolve(res);
                        $rootScope.$broadcast("hideLoading");
                    });

                    return deferred.promise;
                },

                load: function () {
                    var deferred = $q.defer();
                    var _this = this;

                    $rootScope.$broadcast("showLoading");

                    _this.getData().then(function (col) {
                        deferred.resolve(col);
                    });

                    return deferred.promise;
                }
            }
        }]);
    });