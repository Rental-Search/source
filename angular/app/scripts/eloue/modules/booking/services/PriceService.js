define(["angular", "eloue/constants", "eloue/services", "eloue/modules/booking/BookingModule"], function (angular) {
    "use strict";
    /**
     * Price service.
     */
    angular.module("EloueApp.BookingModule").factory("PriceService", ["$rootScope", "$location", "Endpoints", "Prices", function ($rootScope, $location, Endpoints, Prices) {

        return {
            getPricePerDay: function getPricePerDay(productId) {
                return Prices.get({product: productId});
            }
        };
    }]);
});
