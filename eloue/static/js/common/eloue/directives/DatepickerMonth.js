define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    "use strict";
    /**
     * Month+year datepicker component.
     */
    EloueCommon.directive("eloueDatepickerMonth", ['UtilsService', function (UtilsService) {
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
                    language: UtilsService.locale(),
                    // format: "mm/yy",
                    format:{
                        toDisplay: function(date, format, lang){
                            return UtilsService.date(date).format('MM/YY');
                        },
                        toValue: function(date, format, lang){
                            return UtilsService.date(date, 'MM/YY').toDate();
                        }
                    },
                    viewMode: "months",
                    minViewMode: "months",
                    autoclose: true,
                    startDate: Date.today()
                });
            }
        };
    }]);
});
