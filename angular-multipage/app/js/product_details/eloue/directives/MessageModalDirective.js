define(["angular", "eloue/app", "eloue/controllers/ProductDetailsCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display modal window to send message to owner.
     */
    angular.module("EloueApp").directive("eloueMessageModal", [function () {
        return {
            restrict: "E",
            templateUrl: "/partials/product_details/message-modal.html",
            scope: {},
            controller: "ProductDetailsCtrl"
        };
    }]);

});
