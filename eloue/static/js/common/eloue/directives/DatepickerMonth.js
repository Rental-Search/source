define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    "use strict";
    /**
     * Month+year datepicker component.
     */
    EloueCommon.directive("eloueDatepickerMonth", function () {
        return {
            restrict: "A",
            replace: true,
            require: "?ngModel",
            transclude: true,
            link: function (scope, element, attrs, ngModel) {
                if (!ngModel) {
                    return;
                }
                element.datepicker({
                    language: "fr",
                    format: "mm/yy",
                    viewMode: "months",
                    minViewMode: "months",
                    autoclose: true,
                    startDate: Date.today()
                });
            }
        };
    });
});
