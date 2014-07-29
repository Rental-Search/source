define(["angular", "eloue/app", "eloue/controllers/RegisterCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display registration form.
     */
    angular.module("EloueApp").directive("eloueRegistrationForm", ["$window", function ($window) {
        return {
            restrict: "E",
            templateUrl: $window.templatePrefix + "partials/homepage/registration-form.html",
            scope: {},
            controller: "RegisterCtrl"
        };
    }]);
});