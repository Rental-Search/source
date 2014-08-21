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
        EloueCommon.factory("ProductsService", [
            "$q",
            "Products",
            "PicturesService",
            function ($q, Products, PicturesService) {
                var productsService = {};

                productsService.getProduct = function (id) {
                    return Products.get({id: id});
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
                            var hourTime = 60 * 60 * 1000;
                            var dayTime = 24 * hourTime;

                            var startTime = Date.parse(booking.started_at);
                            var endTime = Date.parse(booking.ended_at);

                            var diffTime = endTime - startTime;

                            resultBooking.period_days = Math.round(diffTime / dayTime);
                            resultBooking.period_hours = Math.round((diffTime - dayTime * resultBooking.period_days) / hourTime);

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

                            // Get address
                            var addressId = UtilsService.getIdFromUrl(product.address);
                            productPromises.address = AddressesService.getAddress(addressId).$promise;

                            // Get picture
                            productPromises.pictures = PicturesService.getPicturesByProduct(productId).$promise;

                            // Get phone id
                            resultProduct.phoneId = UtilsService.getIdFromUrl(product.phone);

                            // Get owner id
                            resultProduct.ownerId = UtilsService.getIdFromUrl(product.owner);

                            $q.all(productPromises).then(
                                function (results) {
                                    // Set address
                                    resultProduct.address = {};
                                    resultProduct.address.street = results.address.street;
                                    resultProduct.address.zipcode = results.address.zipcode;
                                    resultProduct.address.city = results.address.city;

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

                                    PhoneNumbersService.getPhoneNumber(product.phoneId).$promise.then(
                                        function (phone) {
                                            bookingDetail.phone = phone.number;
                                            productDeferred.resolve(bookingDetail);
                                        },
                                        function (reason) {
                                            productDeferred.reject(reason);
                                        }
                                    );
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
                                        var author = (value.type == 0) ? booking.owner : booking.borrower;
                                        value.author = author
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

            phoneNumbersService.getPhoneNumber = function (phoneNumbersId) {
                return PhoneNumbers.get({id: phoneNumbersId});
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
                    var hourTime = 60 * 60 * 1000;
                    var dayTime = 24 * hourTime;

                    var startTime = Date.parse(bookingResult.started_at);
                    var endTime = Date.parse(bookingResult.ended_at);

                    var diffTime = endTime - startTime;

                    bookingResult.period_days = Math.round(diffTime / dayTime);
                    bookingResult.period_hours = Math.round((diffTime - dayTime * bookingResult.period_days) / hourTime);

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

            productsParseService.parseProduct = function (productData, addressData, ownerData, phoneData, picturesDataArray) {
                var productResult = angular.copy(productData);

                // Parse address
                if (!!addressData) {
                    productResult.address = addressData;
                }

                // Parse owner
                if (!!ownerData) {
                    productResult.owner = ownerData;
                }

                // Parse phone
                if (!!phoneData) {
                    productResult.phone = phoneData;
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
            function ($q, Bookings, PicturesService, UtilsService, BookingsParseService, ProductsLoadService) {
                var bookingsLoadService = {};

                bookingsLoadService.getBookingList = function (page) {
                    var deferred = $q.defer();

                    // Load bookings
                    Bookings.get({page: page, _cache: new Date().getTime()}).$promise.then(function (bookingListData) {
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
                            deferred.resolve(bookingList);
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
                        ProductsLoadService.getProduct(productId, true, true, true, true).then(function (product) {
                            booking.product = product;
                            deferred.resolve(booking);
                        });
                    });

                    return deferred.promise;
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
            "AddressesService",
            "UsersService",
            "PicturesService",
            "PhoneNumbersService",
            "UtilsService",
            "ProductsParseService",
            function ($q, Products, AddressesService, UsersService, PicturesService, PhoneNumbersService, UtilsService, ProductsParseService) {
                var productLoadService = {};

                productLoadService.getProduct = function (productId, loadAddress, loadOwner, loadPhone, loadPictures) {
                    var deferred = $q.defer();

                    // Load product
                    Products.get({id: productId, _cache: new Date().getTime()}).$promise.then(function (productData) {
                        var productPromises = {};

                        if (loadAddress) {
                            // Get address id
                            var addressId = UtilsService.getIdFromUrl(productData.address);
                            // Load address
                            productPromises.address = AddressesService.getAddress(addressId).$promise;
                        }

                        if (loadOwner) {
                            // Get owner id
                            var ownerId = UtilsService.getIdFromUrl(productData.owner);
                            // Load owner
                            productPromises.owner = UsersService.get(ownerId).$promise;
                        }

                        if (loadPhone) {
                            // Get phone id
                            var phoneId = UtilsService.getIdFromUrl(productData.phone);
                            // Load phone
                            productPromises.phone = PhoneNumbersService.getPhoneNumber(phoneId).$promise;
                        }

                        if (loadPictures) {
                            // Load pictures
                            productPromises.pictures = PicturesService.getPicturesByProduct(productId).$promise;
                        }

                        // When all data loaded
                        $q.all(productPromises).then(function (results) {
                            var product = ProductsParseService.parseProduct(productData, results.address, results.owner,
                                results.phone, (!!results.pictures) ? results.pictures.results : null);
                            deferred.resolve(product);
                        });
                    });

                    return deferred.promise;
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
            function ($q, MessageThreads, UsersService, ProductRelatedMessagesService, UtilsService,
                      MessageThreadsParseService, ProductRelatedMessagesLoadService, ProductsLoadService) {
                var messageThreadsLoadService = {};

                messageThreadsLoadService.getMessageThreadList = function (loadSender, loadLastMessage) {
                    var deferred = $q.defer();

                    // Load message threads
                    MessageThreads.get({_cache: new Date().getTime()}).$promise.then(function (messageThreadListData) {
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

                        $q.all(messageThreadListPromises).then(function (bookingList) {
                            deferred.resolve(bookingList);
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
                        var productId = UtilsService.getIdFromUrl(messageThreadData.product);
                        messageThreadPromises.product = ProductsLoadService.getProduct(productId, true, true, false, true);

                        $q.all(messageThreadPromises).then(function (results) {
                            var messageThread = MessageThreadsParseService.parseMessageThread(messageThreadData, results.messages, results.product);
                            deferred.resolve(messageThread);
                        });
                    });

                    return deferred.promise;
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
                        messageThreadResult.last_message.sent_at = UtilsService.formatDate(lastMessageData.sent_at, "HH'h'mm");
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
            "UsersService",
            "UtilsService",
            "ProductRelatedMessagesParseService",
            function ($q, ProductRelatedMessages, Endpoints, UsersService, UtilsService, ProductRelatedMessagesParseService) {
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

                productRelatedMessagesLoadService.postMessage = function (threadId, recipientId, text, offerid) {
                    var message = {
                        thread: Endpoints.api_url + "messagethreads/" + threadId + "/",
                        recipient: Endpoints.api_url + "users/" + recipientId + "/",
                        body: (!!text) ? text : "",
                        offer: (!!offerid) ? Endpoints.api_url + "bookings/" + offerid + "/" : null
                    };

                    return new ProductRelatedMessages(message).$save();
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
    });