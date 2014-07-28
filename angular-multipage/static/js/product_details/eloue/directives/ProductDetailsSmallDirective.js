define(["angular", "eloue/app", "eloue/controllers/ProductDetailsCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display modal window to call the owner.
     */
    angular.module("EloueApp").directive("eloueProductDetailsSmall", ["$window", function ($window) {
        return {
            restrict: "E",
            templateUrl: $window.templatePrefix + "partials/product_details/product-details-small.html",
            scope: {},
            controller: "ProductDetailsCtrl"
        };
    }]);

});
