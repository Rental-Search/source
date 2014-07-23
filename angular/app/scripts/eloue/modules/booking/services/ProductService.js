define(["angular", "eloue/constants", "eloue/services", "eloue/modules/booking/BookingModule"], function (angular) {
    "use strict";
    /**
     * Product service.
     */
    angular.module("EloueApp.BookingModule").factory("ProductService", ["$rootScope", "$location", "Endpoints", "Products", "CheckAvailability", function ($rootScope, $location, Endpoints, Products, CheckAvailability) {

        return {

            getProduct: function getProduct(id) {
                return Products.get({id: id});
            },

            isAvailable: function isAvailable(id, startDate, endDate, quantity) {
              return CheckAvailability.get({id: id, started_at: startDate, ended_at: endDate, quantity: quantity});
            }
        };
    }]);
});