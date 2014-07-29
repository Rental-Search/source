define(["angular", "eloue/app", "eloue/controllers/LoginCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display login form.
     */
    angular.module("EloueApp").directive("eloueLoginForm", ["$window", function ($window) {
        return {
            restrict: "E",
            templateUrl: $window.templatePrefix + "partials/homepage/login-form.html",
            scope: {},
            controller: "LoginCtrl"
        };
    }]);
    
});