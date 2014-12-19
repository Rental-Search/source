"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Directive to display login form.
     */
    EloueCommon.directive("eloueLoginForm", ["Path", function (Path) {
        return {
            restrict: "E",
            templateUrl: Path.templatePrefix + "partials/homepage/login-form.html",
            scope: {},
            controller: "LoginCtrl"
        };
    }]);
});
