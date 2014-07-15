define(["angular", "eloue/modules/product_details/ProductDetailsModule", "eloue/modules/product_details/controllers/ProductDetailsCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display modal window to call the owner.
     */
    angular.module("EloueApp.ProductDetailsModule").directive("elouePhoneModal", [function () {
        return {
            restrict: "E",
            templateUrl: "/scripts/eloue/modules/product_details/views/phone-modal.html",
            scope: {},
            controller: "ProductDetailsCtrl"
        };
    }]);

});