define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    "use strict";
    /**
     * Datepicker directive.
     */
    EloueCommon.directive("eloueYearDatepicker", ["UtilsService", function (UtilsService) {
        return {
            restrict: "A",
            replace: true,
            require: "?ngModel",
            transclude: true,
            link: function (scope, element, attrs, ngModel) {
                if (!ngModel) return;
                element.datepicker({
                    language: UtilsService.locale(),
                    format:{
                        toDisplay: function(date, format, lang){
                            return UtilsService.date(date).format('L');
                        },
                        toValue: function(date, format, lang){
                            return UtilsService.date(date, 'L').toDate();
                    },
                    autoclose: true,
                    startView: 2,
                    todayHighlight: true,
                    }
                });
            }
        };
    }]);
});
