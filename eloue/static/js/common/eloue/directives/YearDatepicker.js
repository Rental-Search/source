define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    "use strict";
    /**
     * Datepicker directive.
     */
    EloueCommon.directive("eloueYearDatepicker", function () {
        return {
            restrict: "A",
            replace: true,
            require: "?ngModel",
            transclude: true,
            link: function (scope, element, attrs, ngModel) {
                if (!ngModel) return;
                element.datepicker({
                    language: "fr",
                    autoclose: true,
                    startView: 2,
                    todayHighlight: true,
                    dateFormat: "yyyy-MM-dd"
                });
            }
        };
    });
});
