"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Service for managing message threads.
     */
    EloueCommon.factory("MessageThreadsLoadService", [
        "$q",
        "MessageThreads",
        "UtilsService",
        "MessageThreadsParseService",
        "ProductRelatedMessagesLoadService",
        "ProductsLoadService",
        function ($q, MessageThreads, UtilsService, MessageThreadsParseService, ProductRelatedMessagesLoadService, ProductsLoadService) {
            var messageThreadsLoadService = {};

            messageThreadsLoadService.getMessageThreadList = function (page) {
                var deferred = $q.defer();

                // Load message threads
                MessageThreads.get({
                    page: page,
                    ordering: "-last_message__sent_at",
                    _cache: new Date().getTime()
                }).$promise.then(function (messageThreadListData) {
                        var messageThreadListPromises = [];

                        // For each message thread
                        angular.forEach(messageThreadListData.results, function (messageThreadData, key) {
                            var messageThreadDeferred = $q.defer();

                            var messageThread = MessageThreadsParseService.parseMessageThreadListItem(messageThreadData,
                                messageThreadData.last_message);
                            messageThreadDeferred.resolve(messageThread);

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
                MessageThreads.get({
                    id: threadId,
                    _cache: new Date().getTime()
                }).$promise.then(function (messageThreadData) {
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
                        var suppress = function (x) {
                            return x.catch(function () {
                            });
                        };
                        messageThreadPromises.messages = $q.all(messagesPromises.map(suppress));

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
                var senderId = messageThread.sender.id;
                var recipientId = messageThread.recipient.id;

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
});
