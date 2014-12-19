"use strict";
define(["../../../common/eloue/commonApp", "../../../common/eloue/resources"], function (EloueCommon) {
    /**
     * Service for managing prices.
     */
    EloueCommon.factory("PricesService", ["Prices", function (Prices) {
        var pricesService = {};

        pricesService.savePrice = function (price) {
            return Prices.save(price);
        };

        pricesService.updatePrice = function (price) {
            return Prices.update({id: price.id}, price);
        };

        return pricesService;
    }]);
});
