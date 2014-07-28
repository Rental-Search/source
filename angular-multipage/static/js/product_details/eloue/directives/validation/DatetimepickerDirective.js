define(["angular", "eloue/app"], function (angular) {
    "use strict";

    angular.module("EloueApp").directive('eloueDatepicker', function () {
        return {
            restrict: 'A',
            replace: true,
            require: '?ngModel',
            transclude: true,
            link: function (scope, element, attrs, ngModel) {
                if (!ngModel) return;
                element.datepicker();
            }
        };
    });
});
