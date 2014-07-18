define(["angular", "eloue/constants", "eloue/services", "eloue/modules/booking/BookingModule"], function (angular) {
    "use strict";
    /**
     * Product service.
     */
    angular.module("EloueApp.BookingModule").factory("ProductService", ["$rootScope", "$location", "Endpoints", "Products", function ($rootScope, $location, Endpoints, Products) {

        return {

            getProduct: function getProduct(id) {
                //TODO: call real service
                return Products.get({id: id});
            }
        };
    }]);
});