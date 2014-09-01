"use strict";
define(["../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Datepicker directive.
     */
    EloueCommon.directive('eloueDatepicker', function () {
        return {
            restrict: 'A',
            replace: true,
            require: '?ngModel',
            transclude: true,
            link: function (scope, element, attrs, ngModel) {
                if (!ngModel) return;
                element.datepicker();
            }
        };
    });
});