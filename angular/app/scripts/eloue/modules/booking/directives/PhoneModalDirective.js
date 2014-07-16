define(["angular", "eloue/modules/booking/BookingModule", "eloue/modules/booking/controllers/ProductDetailsCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display modal window to call the owner.
     */
    angular.module("EloueApp.BookingModule").directive("elouePhoneModal", [function () {
        return {
            restrict: "E",
            templateUrl: "/scripts/eloue/modules/booking/views/phone-modal.html",
            scope: {},
            controller: "ProductDetailsCtrl"
        };
    }]);

});