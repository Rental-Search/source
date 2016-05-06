define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    "use strict";
    /**
     * Datepicker directive.
     */
    EloueCommon.directive("eloueExtendedDatepicker", ['$translate', function ($translate) {
        return {
            restrict: "A",
            replace: true,
            require: "?ngModel",
            transclude: true,
            link: function (scope, element, attrs, ngModel) {
                if (!ngModel) return;
                element.datepicker({
                    language: $translate.use(),
                    autoclose: true,
                    todayHighlight: true
                });
            }
        };
    }]);
});
