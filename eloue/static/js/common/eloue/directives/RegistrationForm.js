"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Directive to display registration form.
     */
    EloueCommon.directive("eloueRegistrationForm", ["Path", function (Path) {
        return {
            restrict: "E",
            templateUrl: Path.templatePrefix + "partials/homepage/registration-form.html",
            scope: {},
            controller: "RegisterCtrl"
        };
    }]);
});
