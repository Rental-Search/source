define(["angular", "eloue/modules/product_details/ProductDetailsModule", "eloue/modules/product_details/controllers/ProductDetailsCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display modal window with booking details.
     */
    angular.module("EloueApp.ProductDetailsModule").directive("eloueBookingModal", [function () {
        return {
            restrict: "E",
            templateUrl: "/scripts/eloue/modules/product_details/views/booking-modal.html",
            scope: {},
            controller: "ProductDetailsCtrl"
        };
    }]);

});