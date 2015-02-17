define(["../../../common/eloue/commonApp", "../../../common/eloue/resources",
    "../../../common/eloue/services/UsersService",
    "../../../common/eloue/services/UtilsService"], function (EloueCommon) {
    "use strict";
    /**
     * Service for managing product related messages.
     */
    EloueCommon.factory("ProductRelatedMessagesService", [
        "$q",
        "ProductRelatedMessages",
        "Endpoints",
        "MessageThreads",
        "UsersService",
        "UtilsService",
        function ($q, ProductRelatedMessages, Endpoints, MessageThreads, UsersService, UtilsService) {
            var productRelatedMessagesService = {};

            productRelatedMessagesService.getMessage = function (id) {
                return ProductRelatedMessages.get({id: id, _cache: new Date().getTime()}).$promise;
            };

            productRelatedMessagesService.getMessageListItem = function (messageId) {
                var deferred = $q.defer();

                this.getMessage(messageId).then(function (messageData) {
                    var message = productRelatedMessagesService.parseMessage(messageData, messageData.sender);
                    deferred.resolve(message);
                }, function (reason) {
                    deferred.reject(reason);
                });
                return deferred.promise;
            };

            productRelatedMessagesService.postMessage = function (threadId, senderId, recipientId, text, offerId, productId) {
                var threadDef = $q.defer(), messageThread, deferred;
                if (!threadId) {
                    messageThread = {
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
                deferred = $q.defer();
                threadDef.promise.then(function (result) {
                    var message = {
                        thread: Endpoints.api_url + "messagethreads/" + result + "/",
                        sender: Endpoints.api_url + "users/" + senderId + "/",
                        recipient: Endpoints.api_url + "users/" + recipientId + "/",
                        body: text || "",
                        offer: offerId ? Endpoints.api_url + "bookings/" + offerId + "/" : null
                    };
                    ProductRelatedMessages.save(message).$promise.then(function (response) {
                        var responseSenderId = UtilsService.getIdFromUrl(response.sender);
                        UsersService.get(responseSenderId).then(function (result) {
                            response.sender = result;
                            deferred.resolve(response);
                        });
                    });
                });
                return deferred.promise;
            };

            productRelatedMessagesService.updateMessage = function (message) {
                return ProductRelatedMessages.update({id: message.id}, message).$promise;
            };

            productRelatedMessagesService.markAsRead = function (messageId) {
                return ProductRelatedMessages.seen({id: messageId}, {id: messageId}).$promise;
            };

            productRelatedMessagesService.parseMessage = function (messageData, senderData) {
                var messageResults = angular.copy(messageData);

                // Parse sender
                if (senderData) {
                    messageResults.sender = senderData;
                }
                return messageResults;
            };

            return productRelatedMessagesService;
        }
    ]);
});
