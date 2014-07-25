define(["angular", "eloue/app", "eloue/controllers/ProductDetailsCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display modal window with booking details.
     */
    angular.module("EloueApp").directive("eloueBookingModal", [function () {
        return {
            restrict: "E",
            templateUrl: "/partials/product_details/booking-modal.html",
            scope: {},
            controller: "ProductDetailsCtrl"
        };
    }]);

});