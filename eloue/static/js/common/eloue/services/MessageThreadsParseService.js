"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Service for parsing message threads.
     */
    EloueCommon.factory("MessageThreadsParseService", [
        "UtilsService",
        function (UtilsService) {
            var messageThreadsParseService = {};

            messageThreadsParseService.parseMessageThreadListItem = function (messageThreadData, lastMessageData) {
                var messageThreadResult = angular.copy(messageThreadData);

                // Parse last message
                if (!!lastMessageData) {
                    // if the creation date of the last message is the current day display only the hour
                    // if the creation date of the last message is before the current day display the date and not the hour
                    if (UtilsService.isToday(lastMessageData.sent_at)) {
                        messageThreadResult.last_message.sent_at = UtilsService.formatDate(lastMessageData.sent_at, "HH'h'mm");
                    } else {
                        messageThreadResult.last_message.sent_at = UtilsService.formatDate(lastMessageData.sent_at, "dd.MM.yyyy");
                    }
                }

                return messageThreadResult;
            };

            messageThreadsParseService.parseMessageThread = function (messageThreadData, messagesDataArray, productData) {
                var messageThreadResult = angular.copy(messageThreadData);

                // Parse messages
                if (!!messagesDataArray) {
                    messageThreadResult.messages = messagesDataArray;
                    var messageKeysToRemove = [];
                    angular.forEach(messageThreadResult.messages, function (message, key) {
                        if (!!message) {
                            message.sent_at = UtilsService.formatDate(message.sent_at, "dd.MM.yyyy HH'h'mm");
                        } else {
                            messageKeysToRemove.push(key);
                        }
                    });
                    angular.forEach(messageKeysToRemove, function (index, key) {
                        messageThreadResult.messages.splice(index, 1);
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
});
