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
                element.datetimepicker().on("change", function (event) {
                    var date = new Date(Date.parse($(event.target).val()));
                    var currentDate = new Date();

                    scope.$apply(function () {
                        ngModel.$setViewValue(date.toString("dd/MM/yyyy hh:mm"));
                    });
                    // Check if selected date is in future
                    var pastDate = date.getTime() > currentDate.getTime();
                    ngModel.$setValidity("pastDate", pastDate);
                });
            }
        };
    });
});
