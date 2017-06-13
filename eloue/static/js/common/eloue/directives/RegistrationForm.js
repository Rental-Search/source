define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    "use strict";
    /**
     * Directive to display registration form.
     */
    EloueCommon.directive("eloueRegistrationForm", ["Path", function (Path) {
        return {
            restrict: "E",
            templateUrl: Path.templatePrefix + "partials/homepage/registration-form.html",
            scope: {},
            controller: "RegisterCtrl",
            link: function (scope, element, attrs, ngModel) {
                var link = document.getElementById('registration-link');
                analytics.trackLink(link, "Signed Up Modal");
            }
        };
    }]);
});
