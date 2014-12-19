"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
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
