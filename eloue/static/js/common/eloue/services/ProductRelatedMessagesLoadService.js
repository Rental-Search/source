"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
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
                    var message = ProductRelatedMessagesParseService.parseMessage(messageData, messageData.sender);
                    deferred.resolve(message);
                }, function (reason) {
                    deferred.reject(reason);
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
                    ProductRelatedMessages.save(message).$promise.then(function (response) {
                        var responseSenderId = UtilsService.getIdFromUrl(response.sender);
                        UsersService.get(responseSenderId).$promise.then(function (result) {
                            response.sender = result;
                            deferred.resolve(response);
                        });
                    });
                });
                return deferred.promise;
            };

            productRelatedMessagesLoadService.updateMessage = function (message) {
                return ProductRelatedMessages.update({id: message.id}, message);
            };


            return productRelatedMessagesLoadService;
        }
    ]);
});
