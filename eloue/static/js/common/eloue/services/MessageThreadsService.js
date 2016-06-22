define(["../../../common/eloue/commonApp", "../../../common/eloue/resources", "../../../common/eloue/values",
    "../../../common/eloue/services/ProductsService",
    "../../../common/eloue/services/ProductRelatedMessagesService",
    "../../../common/eloue/services/UtilsService"], function (EloueCommon) {
    "use strict";
    /**
     * Service for managing message threads.
     */
    EloueCommon.factory("MessageThreadsService", [
        "$q",
        "MessageThreads",
        "ProductsService",
        "ProductRelatedMessagesService",
        "UtilsService",
        function ($q, MessageThreads, ProductsService, ProductRelatedMessagesService, UtilsService) {
            var messageThreadsService = {};

            messageThreadsService.getMessageThreadByProductAndParticipant = function (productId, participantId) {
                var deferred = $q.defer();
                MessageThreads.list({
                    product: productId,
                    empty: "False",
                    participant: participantId,
                    _cache: new Date().getTime()
                }).$promise.then(
                    function (result) {
                        var promises = {
                            // Add thread details to the final result.
                            threads: result.$promise
                        };

                        // If thread exits, load messages for this thread.
                        if (result.results.length > 0) {
                            promises.messages = ProductRelatedMessagesService.getThreadMessages(result.results[0].id)
                        }

                        $q.all(promises).then(function success(results) {
                            deferred.resolve(results);
                        });
                    }
                );
                return deferred.promise;
            };
            
            messageThreadsService.isThreadSeen = function(threadId) {
                return MessageThreads.isThreadSeen({id: threadId}).$promise;
            };

            messageThreadsService.getMessageThreadList = function (page) {
                var deferred = $q.defer();

                // Load message threads
                MessageThreads.get({
                    page: page,
                    empty: "False",
                    ordering: "-last_message__sent_at",
                    _cache: new Date().getTime()
                }).$promise.then(
                    function (messageThreadListData) {
                        var messageThreadListPromises = [];

                        // For each message thread
                        angular.forEach(messageThreadListData.results, function (messageThreadData, key) {
                            var messageThreadDeferred = $q.defer();

                            var messageThread = messageThreadsService.parseMessageThreadListItem(messageThreadData,
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
                    }
                );
                return deferred.promise;
            };

            messageThreadsService.getMessageThreadById = function (threadId) {
                var deferred = $q.defer();

                // Load message thread
                MessageThreads.get({
                    id: threadId,
                    _cache: new Date().getTime()
                }).$promise.then(
                    function (messageThreadData) {
                        var messageThreadPromises = {};

                        // Load messages
                        var messagesPromises = [];
                        messagesPromises.push(ProductRelatedMessagesService.getThreadMessages(messageThreadData.id));

                        // When all messages loaded
                        var suppress = function (x) {
                            return x.catch(function () {
                            });
                        };
                        messageThreadPromises.messages = $q.all(messagesPromises.map(suppress));

                        // Get product id
                        if (messageThreadData.product) {
                            var productId = UtilsService.getIdFromUrl(messageThreadData.product);
                            messageThreadPromises.product = ProductsService.getProduct(productId, true, true);
                        }

                        $q.all(messageThreadPromises).then(function (results) {
                            var messages = (results.messages && results.messages[0]) ? results.messages[0].results : undefined;
                            var messageThread = messageThreadsService.parseMessageThread(messageThreadData, messages, results.product);
                            deferred.resolve(messageThread);
                        });
                    }
                );
                return deferred.promise;
            };

            messageThreadsService.getUsersRoles = function (messageThread, currentUserId) {
                var senderId = messageThread.sender.id,
                    recipientId = messageThread.recipient.id,
                    result = {
                        senderId: currentUserId
                    };

                if (senderId === currentUserId) {
                    result.recipientId = recipientId;
                } else {
                    result.recipientId = senderId;
                }

                return result;
            };

            messageThreadsService.parseMessageThreadListItem = function (messageThreadData, lastMessageData) {
                var messageThreadResult = angular.copy(messageThreadData);

                // Parse last message
                if (lastMessageData) {
                    // if the creation date of the last message is the current day display only the hour
                    // if the creation date of the last message is before the current day display the date and not the hour
                    if (UtilsService.isToday(lastMessageData.sent_at)) {
                        messageThreadResult.last_message.sent_at = UtilsService.date(lastMessageData.sent_at).format("LT");
                    } else {
                        messageThreadResult.last_message.sent_at = UtilsService.date(lastMessageData.sent_at).format("lll");
                    }
                }
                return messageThreadResult;
            };

            messageThreadsService.parseMessageThread = function (messageThreadData, messagesDataArray, productData) {
                var messageThreadResult = angular.copy(messageThreadData), messageKeysToRemove;

                // Parse messages
                if (messagesDataArray) {
                    messageThreadResult.messages = messagesDataArray;
                    messageKeysToRemove = [];
                    angular.forEach(messageThreadResult.messages, function (message, key) {
                        if (message) {
                            message.sent_at = UtilsService.date(message.sent_at).format("L LT");
                        } else {
                            messageKeysToRemove.push(key);
                        }
                    });
                    angular.forEach(messageKeysToRemove, function (index, key) {
                        messageThreadResult.messages.splice(index, 1);
                    });
                    messageThreadResult.messagesCount = messageThreadData.messages.length;
                }

                // Parse product
                if (productData) {
                    messageThreadResult.product = productData;
                }
                return messageThreadResult;
            };

            return messageThreadsService;
        }
    ]);
});
