define(["angular", "eloue/modules/booking/BookingModule", "eloue/modules/booking/controllers/ProductDetailsCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display modal window with booking details.
     */
    angular.module("EloueApp.BookingModule").directive("eloueBookingModal", ["$window", function ($window) {
        return {
            restrict: "E",
            templateUrl: $window.templatePrefix + "partials/product_details/booking-modal.html",
            scope: {},
            controller: "ProductDetailsCtrl"
        };
    }]);
});