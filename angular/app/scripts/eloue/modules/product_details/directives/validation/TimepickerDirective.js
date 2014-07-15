define(["angular", "eloue/modules/product_details/ProductDetailsModule"], function (angular) {
    "use strict";

    angular.module("EloueApp.ProductDetailsModule").directive('eloueTimepicker', function () {
        return {
            restrict: 'A',
            replace: true,
            require: '?ngModel',
            transclude: true,
            link: function (scope, element, attrs, ngModel) {
                if (!ngModel) return;
                element.timepicker().on("changeTime", function (event) {
                });
            }
        };
    });
});