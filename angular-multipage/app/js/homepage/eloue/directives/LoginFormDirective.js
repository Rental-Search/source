/**
 * Created by mbaev on 09.07.2014.
 */
define(["angular", "eloue/app", "eloue/controllers/LoginCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display login form.
     */
    angular.module("EloueApp").directive("eloueLoginForm", [function () {
        return {
            restrict: "E",
            templateUrl: "/partials/homepage/login-form.html",
            scope: {},
            controller: "LoginCtrl"
        };
    }]);
    
});