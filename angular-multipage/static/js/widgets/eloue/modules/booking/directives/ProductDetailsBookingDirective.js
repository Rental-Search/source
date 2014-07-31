define(["angular", "eloue/modules/booking/BookingModule", "eloue/modules/booking/controllers/ProductDetailsCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display booking form on product details page.
     */
    angular.module("EloueApp.BookingModule").directive("eloueProductDetailsBooking", ["$window", function ($window) {
        return {
            restrict: "E",
            templateUrl: $window.templatePrefix + "partials/product_details/product-details-booking.html",
            scope: {
                inModal: "=inModal",
                inBooking: "=inBooking",
                inMessage: "=inMessage"
            },
            controller: "ProductDetailsCtrl"
        };
    }]);
});