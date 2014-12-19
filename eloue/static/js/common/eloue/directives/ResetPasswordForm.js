"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Directive to display reset password form.
     */
    EloueCommon.directive("eloueResetPasswordForm", ["Path", function (Path) {
        return {
            restrict: "E",
            templateUrl: Path.templatePrefix + "partials/homepage/reset-password-form.html",
            scope: {},
            controller: "ResetPasswordCtrl"
        };
    }]);
});
