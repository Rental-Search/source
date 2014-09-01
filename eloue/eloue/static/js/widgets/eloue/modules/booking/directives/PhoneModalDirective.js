define(["angular", "eloue/modules/booking/BookingModule", "eloue/modules/booking/controllers/ProductDetailsCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display modal window to call the owner.
     */
    angular.module("EloueApp.BookingModule").directive("elouePhoneModal", ["$window", function ($window) {
        return {
            restrict: "E",
            templateUrl: $window.templatePrefix + "partials/product_details/phone-modal.html",
            scope: {},
            controller: "ProductDetailsCtrl"
        };
    }]);
});