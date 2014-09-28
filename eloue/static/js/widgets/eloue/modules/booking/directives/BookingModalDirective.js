define(["angular", "eloue/modules/booking/BookingModule", "eloue/modules/booking/controllers/ProductDetailsCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display modal window with booking details.
     */
    angular.module("EloueApp.BookingModule").directive("eloueBookingModal", ["Path", function (Path) {
        return {
            restrict: "E",
            templateUrl: Path.templatePrefix + "partials/product_details/booking-modal.html",
            scope: {},
            controller: "ProductDetailsCtrl"
        };
    }]);
});