define(["angular", "eloue/app", "eloue/controllers/ProductDetailsCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display booking form on product details page.
     */
    angular.module("EloueApp").directive("eloueProductDetailsBooking", ["$window", function ($window) {
        return {
            restrict: "E",
            templateUrl: $window.templatePrefix + "partials/product_details/product-details-booking.html",
            scope: {
                inModal: "=inModal",
                inBooking: "=inBooking"
            },
            controller: "ProductDetailsCtrl"
        };
    }]);

});