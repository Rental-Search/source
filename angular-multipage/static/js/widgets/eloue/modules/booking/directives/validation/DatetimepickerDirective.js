define(["angular", "eloue/modules/booking/BookingModule"], function (angular) {
    "use strict";

    angular.module("EloueApp.BookingModule").directive('eloueDatepicker', function () {
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
