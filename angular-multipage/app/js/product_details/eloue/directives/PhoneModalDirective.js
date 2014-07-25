define(["angular", "eloue/app", "eloue/controllers/ProductDetailsCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display modal window to call the owner.
     */
    angular.module("EloueApp").directive("elouePhoneModal", [function () {
        return {
            restrict: "E",
            templateUrl: "/partials/product_details/phone-modal.html",
            scope: {},
            controller: "ProductDetailsCtrl"
        };
    }]);

});