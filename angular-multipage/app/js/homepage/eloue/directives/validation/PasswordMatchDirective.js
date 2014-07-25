define(["angular", "eloue/app"], function (angular) {

    "use strict";

    /**
     * Directive to validate password confirmation.
     */
    angular.module("EloueApp").directive("elouePasswordMatch", ["$parse", function ($parse) {
        return {
            restrict: "A",
            require: "ngModel",
            link: function (scope, element, attrs, ngModel) {
                ngModel.$parsers.unshift(function (viewValue, $scope) {
                    var noMatch = viewValue != scope.registrationForm.password.$viewValue;
                    ngModel.$setValidity("noMatch", !noMatch);
                    return viewValue;
                })
            }
        }
    }]);
});