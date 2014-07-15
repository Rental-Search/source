define(["angular", "eloue/modules/product_details/ProductDetailsModule", "eloue/modules/product_details/controllers/ProductDetailsCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display booking form on product details page.
     */
    angular.module("EloueApp.ProductDetailsModule").directive("eloueProductDetailsBooking", [function () {
        return {
            restrict: "E",
            templateUrl: "/scripts/eloue/modules/product_details/views/partials/product-details-booking.html",
            scope: {},
            controller: "ProductDetailsCtrl"
        };
    }]);

});