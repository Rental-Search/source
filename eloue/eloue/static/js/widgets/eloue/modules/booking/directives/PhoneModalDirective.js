define(["angular", "eloue/modules/booking/BookingModule", "eloue/modules/booking/controllers/ProductDetailsCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display modal window to call the owner.
     */
    angular.module("EloueApp.BookingModule").directive("elouePhoneModal", ["Path", function (Path) {
        return {
            restrict: "E",
            templateUrl: Path.templatePrefix + "partials/product_details/phone-modal.html",
            scope: {},
            controller: "ProductDetailsCtrl"
        };
    }]);
});