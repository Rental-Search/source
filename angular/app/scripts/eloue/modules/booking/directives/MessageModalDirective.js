define(["angular", "eloue/modules/booking/BookingModule", "eloue/modules/booking/controllers/ProductDetailsCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display modal window to send message to owner.
     */
    angular.module("EloueApp.BookingModule").directive("eloueMessageModal", [function () {
        return {
            restrict: "E",
            templateUrl: "/scripts/eloue/modules/booking/views/message-modal.html",
            scope: {},
            controller: "ProductDetailsCtrl"
        };
    }]);

});
