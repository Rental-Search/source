define(["angular", "eloue/resources", "eloue/modules/booking/BookingModule"], function (angular) {
    "use strict";
    /**
     * Price service.
     */
    angular.module("EloueApp.BookingModule").factory("PriceService", ["Prices", function (Prices) {

        return {
            getPricePerDay: function getPricePerDay(productId) {
                return Prices.get({product: productId});
            }
        };
    }]);
});
