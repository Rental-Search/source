"use strict";
define(["../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Datepicker directive.
     */
    EloueCommon.directive('eloueDatepicker', function () {
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

    /**
     * Directive to display registration form.
     */
    EloueCommon.directive("eloueRegistrationForm", ["$window", function ($window) {
        return {
            restrict: "E",
            templateUrl: $window.templatePrefix + "partials/homepage/registration-form.html",
            scope: {},
            controller: "RegisterCtrl"
        };
    }]);

    /**
     * Directive to display login form.
     */
    EloueCommon.directive("eloueLoginForm", ["$window", function ($window) {
        return {
            restrict: "E",
            templateUrl: $window.templatePrefix + "partials/homepage/login-form.html",
            scope: {},
            controller: "LoginCtrl"
        };
    }]);
});