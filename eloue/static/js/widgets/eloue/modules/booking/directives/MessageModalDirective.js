define(["angular", "eloue/modules/booking/BookingModule", "eloue/modules/booking/controllers/ProductDetailsCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display modal window to send message to owner.
     */
    angular.module("EloueApp.BookingModule").directive("eloueMessageModal", ["Path", function (Path) {
        return {
            restrict: "E",
            templateUrl: Path.templatePrefix + "partials/product_details/message-modal.html",
            scope: {},
            controller: "ProductDetailsCtrl"
        };
    }]);
});
