define(["angular", "eloue/constants", "eloue/modules/booking/BookingModule"], function (angular) {
    "use strict";
    /**
     * Price service.
     */
    angular.module("EloueApp.BookingModule").factory("PriceService", ["$rootScope", "$location", "Endpoints", function ($rootScope, $location, Endpoints) {

        return {
            getPricePerDay: function getPricePerDay(productId) {
                console.log(1);
return 12;
            }
        };
    }]);
});
