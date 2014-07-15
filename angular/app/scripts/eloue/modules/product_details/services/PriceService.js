define(["angular", "eloue/constants", "eloue/modules/product_details/ProductDetailsModule"], function (angular) {
    "use strict";
    /**
     * Price service.
     */
    angular.module("EloueApp.ProductDetailsModule").factory("PriceService", ["$rootScope", "$location", "Endpoints", function ($rootScope, $location, Endpoints) {

        return {
            getPricePerDay: function getPricePerDay(productId) {
                console.log(1);
return 12;
            }
        };
    }]);
});
