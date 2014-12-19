"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Service for managing message threads.
     */
    EloueCommon.factory("MessageThreadsService", [
        "$q",
        "MessageThreads",
        "ProductRelatedMessagesService",
        "UtilsService",
        function ($q, MessageThreads, ProductRelatedMessagesService, UtilsService) {
            var messageThreadsService = {};

            messageThreadsService.getMessageThread = function (productId, participantId) {
                var deferred = $q.defer();
                MessageThreads.list({
                    product: productId,
                    participant: participantId,
                    _cache: new Date().getTime()
                }).$promise.then(function (result) {
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

            return messageThreadsService;
        }
    ]);
});
