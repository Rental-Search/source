define(["angular", "eloue/modules/booking/BookingModule", "eloue/modules/booking/controllers/ProductDetailsCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display booking form on product details page.
     */
    angular.module("EloueApp.BookingModule").directive("eloueProductDetailsBooking", [function () {
        return {
            restrict: "E",
            templateUrl: "/scripts/eloue/modules/booking/views/partials/product-details-booking.html",
            scope: {
                inModal: "=inModal"
            },
            controller: "ProductDetailsCtrl"
        };
    }]);

});