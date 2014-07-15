define(["angular", "eloue/modules/product_details/ProductDetailsModule"], function (angular) {
    "use strict";

    angular.module("EloueApp.ProductDetailsModule").directive('eloueDatepicker', function () {
        return {
            restrict: 'A',
            replace: true,
            require: '?ngModel',
            transclude: true,
            link: function (scope, element, attrs, ngModel) {
                if (!ngModel) return;
                element.datepicker().on("changeDate", function (event) {
                    console.log(attrs.name);
                    var date = event.date;
                    var day = date.getDate();
                    var month = date.getMonth() + 1;
                    var year = date.getFullYear();

                    var currentDate = new Date();
                    var currentYear = currentDate.getFullYear();
                    var currentDay = currentDate.getDate();
                    var currentMonth = currentDate.getMonth() + 1;

                    scope.$apply(function () {
                        ngModel.$setViewValue(day + "/" + month + "/" + year);
                    });
                    // Check if selected date is in future
                    var pastDate = date.getTime() > currentDate.getTime();
                    ngModel.$setValidity("pastDate", pastDate);
                });
            }
        };
    });
});
