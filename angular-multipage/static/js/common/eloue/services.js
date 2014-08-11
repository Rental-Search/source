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
            "UtilsService",
            function ($q, $filter, MessageThreads, ProductRelatedMessagesService, UsersService, UtilsService) {
                var messageThreadsService = {};

                /**
                 * Retrieves list of message threads.
                 *
                 * @returns list of message threads
                 */
                messageThreadsService.getMessageThreads = function () {
                    var self = this;
                    var deferred = $q.defer();

                    MessageThreads.get({}).$promise.then(function (threads) {
                        var promises = [];

                        // For each message thread
                        angular.forEach(threads.results, function (value, key) {
                            var result = {
                                id: value.id,
                                subject: value.subject
                            };

                            var threadDeferred = $q.defer();
                            var threadPromises = [];

                            // Get last message
                            var messageId = self.getIdFromUrl(value.last_message);
                            threadPromises.push(ProductRelatedMessagesService.getMessage(messageId).$promise);

                            // Get sender
                            var senderId = self.getIdFromUrl(value.sender);
                            threadPromises.push(UsersService.get(senderId).$promise);

                            // Set information in the result object
                            $q.all(threadPromises).then(function (threadResults) {
                                result.message = threadResults[0].body;
                                result.icon = threadResults[1].avatar.thumbnail;
                                result.username = threadResults[1].slug;
                                result.date = UtilsService.formatMessageDate(threadResults[0].sent_at,
                                    "HH'h'mm", "dd.mm.yyyy HH'h'mm");

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
                 * Retrieves list messages for a specific thread.
                 *
                 * @param threadId identifier of a thread
                 */
                messageThreadsService.getMessages = function (threadId) {
                    var self = this;
                    var deferred = $q.defer();

                    MessageThreads.get({id: threadId}).$promise.then(function (thread) {
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
                                    result.username = sender.slug;
                                    result.icon = sender.avatar.thumbnail;
                                    messageDeferred.resolve(result);
                                });
                            });

                            promises.push(messageDeferred.promise);
                        });

                        $q.all(promises).then(function (results) {
                            deferred.resolve(results);
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
        EloueCommon.factory("ProductRelatedMessagesService", ["ProductRelatedMessages", function (ProductRelatedMessages) {
            var productRelatedMessagesService = {};

            productRelatedMessagesService.getMessage = function (id) {
                return ProductRelatedMessages.get({id: id});
            };

            return productRelatedMessagesService;
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

            return utilsService;
        }]);
    });