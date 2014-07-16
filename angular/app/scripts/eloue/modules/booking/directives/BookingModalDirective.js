define(["angular", "eloue/modules/booking/BookingModule", "eloue/modules/booking/controllers/ProductDetailsCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display modal window with booking details.
     */
    angular.module("EloueApp.BookingModule").directive("eloueBookingModal", [function () {
        return {
            restrict: "E",
            templateUrl: "/scripts/eloue/modules/booking/views/booking-modal.html",
            scope: {},
            controller: "ProductDetailsCtrl"
        };
    }]);

});