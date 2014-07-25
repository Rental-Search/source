define(["angular", "eloue/app", "eloue/controllers/ProductDetailsCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display booking form on product details page.
     */
    angular.module("EloueApp").directive("eloueProductDetailsBooking", [function () {
        return {
            restrict: "E",
            templateUrl: "/partials/product_details/product-details-booking.html",
            scope: {
                inModal: "=inModal",
                inBooking: "=inBooking"
            },
            controller: "ProductDetailsCtrl"
        };
    }]);

});