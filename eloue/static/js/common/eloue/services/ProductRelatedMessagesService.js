"use strict";
define(["../../../common/eloue/commonApp", "../../../common/eloue/resources"], function (EloueCommon) {
    /**
     * Service for managing product related messages.
     */
    EloueCommon.factory("ProductRelatedMessagesService", [
        "ProductRelatedMessages",
        function (ProductRelatedMessages) {
            var productRelatedMessagesService = {};

            productRelatedMessagesService.getMessage = function (id) {
                return ProductRelatedMessages.get({id: id, _cache: new Date().getTime()});
            };

            return productRelatedMessagesService;
        }
    ]);
});
