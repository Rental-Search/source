/**
 * Created by mbaev on 09.07.2014.
 */
define(["angular", "eloue/app", "eloue/controllers/RegisterCtrl"], function (angular) {
    "use strict";

    /**
     * Directive to display registration form.
     */
    angular.module("EloueApp").directive("eloueRegistrationForm", [function () {
        return {
            restrict: "E",
            templateUrl: "/partials/homepage/registration-form.html",
            scope: {},
            controller: "RegisterCtrl"
        };
    }]);
});