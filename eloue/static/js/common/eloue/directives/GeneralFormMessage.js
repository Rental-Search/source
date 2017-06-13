define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    "use strict";
    /**
     * Directive to show global error message for form.
     * If it's have not message set ng-hide to container.
     */
    EloueCommon.directive("eloueGeneralFormMessage", ["$animate", "ServerValidationService", function ($animate, ServerValidationService) {
        return {
            restrict: "A",
            scope: true,
            link: function (scope, element, attrs) {
                var formTag = attrs.formTag;
                scope.$watchCollection(function () {
                    return ServerValidationService.getFormErrorMessage(formTag);
                }, function (value) {
                    if (!!value) {
                        scope.message = value.message;
                        scope.description = value.description;
                        scope.errors = value.errors;

                        if (scope.errors && !angular.isObject(scope.errors)) {
                            element.text(scope.errors);
                            $animate["removeClass"](element, "ng-hide");
                        }
                    } else {
                        $animate["addClass"](element, "ng-hide");
                    }
                });
            }
        };
    }]);
});
