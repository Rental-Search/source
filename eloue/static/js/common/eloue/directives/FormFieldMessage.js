define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    "use strict";
    /**
     * Directive to show field error message for form's field.
     * If it's have not message set ng-hide to container.
     */
    EloueCommon.directive("eloueFormFieldMessage", ["$animate", "ServerValidationService", function ($animate, ServerValidationService) {
        return {
            restrict: "A",
            scope: true,
            link: function (scope, element, attrs) {
                var formTag, fieldName;
                formTag = attrs.formTag;
                fieldName = attrs.fieldName;
                if (!!fieldName) {
                    scope.$watch(function () {
                        return ServerValidationService.getFieldError(fieldName, formTag);
                    }, function (value) {
                        if (!!value) {
                            $animate["removeClass"](element, "ng-hide");
                            scope.value = value[0];
                        } else {
                            $animate["addClass"](element, "ng-hide");
                        }
                    });
                }
            }
        };
    }]);
});
