define(["angular", "eloue/constants", "eloue/resources", "eloue/modules/booking/BookingModule"], function (angular) {
    "use strict";
    /**
     * Call service.
     */
    angular.module("EloueApp.BookingModule").factory("MessageService", ["$q", "Endpoints", "MessageThreads", "ProductRelatedMessages", "Users", function ($q, Endpoints, MessageThreads, ProductRelatedMessages, Users) {

        return {
            getMessageThread: function getMessageThread(productId) {
                var deferred = $q.defer();
                var self = this;
                MessageThreads.list({product: productId}).$promise.then(function (result) {
                    var promises = [];
                    angular.forEach(result.results, function (value, key) {
                        angular.forEach(value.messages, function (messageLink, idx) {
                            var messageId = self.getIdFromUrl(messageLink);
                            promises.push(ProductRelatedMessages.get({id: messageId}).$promise);
                        });
                    });
                    $q.all(promises).then(function success(results) {
                        deferred.resolve(results);
                    });
                });
                return deferred.promise;
            },

            sendMessage: function sendMessage(message, productId) {

                var threadDef = $q.defer();
                var self = this;
                if (!message.thread) {
                    var messageThread = {
                        "sender": message.sender,
                        "recipient": message.recipient,
                        "product": Endpoints.api_url + "products/" + productId + "/",
                        "subject": "Question",
                        "sender_archived": false,
                        "recipient_archived": false,
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
                        var senderId = self.getIdFromUrl(response.sender);
                        Users.get({id: senderId}).$promise.then(function (result) {
                            response.sender = result;
                            deferred.resolve(response);
                        });
                    });
                });
                return deferred.promise;
            },

            getIdFromUrl: function getIdFromUrl(url) {
                var trimmedUrl = url.slice(0, url.length - 1);
                return trimmedUrl.substring(trimmedUrl.lastIndexOf("/") + 1, url.length);
            }
        };
    }]);
});
