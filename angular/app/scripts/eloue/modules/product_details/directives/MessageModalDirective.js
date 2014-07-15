define(["angular", "eloue/modules/product_details/ProductDetailsModule", "eloue/modules/product_details/controllers/ProductDetailsCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display modal window to send message to owner.
     */
    angular.module("EloueApp.ProductDetailsModule").directive("eloueMessageModal", [function () {
        return {
            restrict: "E",
            templateUrl: "/scripts/eloue/modules/product_details/views/message-modal.html",
            scope: {},
            controller: "ProductDetailsCtrl"
        };
    }]);

});
