define(["angular", "eloue/app", "eloue/resources"], function (angular) {
    "use strict";
    /**
     * Price service.
     */
    angular.module("EloueApp").factory("PriceService", ["Prices", function (Prices) {

        return {

            /**
             * Get product price per day.
             * @param productId product ID
             * @returns Price
             */
            getPricePerDay: function getPricePerDay(productId) {
                return Prices.get({product: productId});
            }
        };
    }]);
});
