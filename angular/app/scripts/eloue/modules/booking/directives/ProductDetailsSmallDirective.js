define(["angular", "eloue/modules/booking/BookingModule", "eloue/modules/booking/controllers/ProductDetailsCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display modal window to call the owner.
     */
    angular.module("EloueApp.BookingModule").directive("eloueProductDetailsSmall", [function () {
        return {
            restrict: "E",
            templateUrl: "/scripts/eloue/modules/booking/views/partials/product-details-small.html",
            scope: {},
            controller: "ProductDetailsCtrl"
        };
    }]);

});
