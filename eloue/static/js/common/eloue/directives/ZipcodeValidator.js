define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    "use strict";

    /**
     * Directive to validate zipcode.
     */

    // Regexp to validate zipcode. Must contain 5 numbers.
    var ZIPCODE_REGEXP = /\b[0-9]{5}\b/;

    //TODO fix eloue/templates/jade/pop_up_sections/_personal_information_form.jade
    EloueCommon.directive("eloueZipcode", function () {
        return {
            restrict: "A",
            require: "ngModel",
            link: function (scope, elem, attrs, ctrl) {
                ctrl.$parsers.unshift(function (viewValue) {
                    if (0 === viewValue.length) {
                        // Prevent two messages at the same time.
                        ctrl.$setValidity("badFormat", true);
                    } else {
                        ctrl.$setValidity("badFormat", ZIPCODE_REGEXP.test(viewValue));
                    }
                    return viewValue;
                });
            }
        };
    });
});
