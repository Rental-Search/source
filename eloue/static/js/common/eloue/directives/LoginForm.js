define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    "use strict";
    /**
     * Directive to display login form.
     */
    EloueCommon.directive("eloueLoginForm", ["Path", function (Path) {
        return {
            restrict: "E",
            templateUrl: Path.templatePrefix + "partials/homepage/login-form.html",
            scope: {},
            controller: "LoginCtrl",
            link: function (scope, element, attrs, ngModel) {
                var link = document.getElementById('login-link');
                analytics.trackLink(link, "Sign In Modal");
            }
        };
    }]);
});
