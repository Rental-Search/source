"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Directive to show global error message for form.
     * If it's have not message set ng-hide to container.
     */
    EloueCommon.directive("eloueFormMessage", ["$animate", "ServerValidationService", function ($animate, ServerValidationService) {
        return {
            restrict: "A",
            scope: true,
            link: function (scope, element, attrs) {
                var formTag = attrs.formTag;
                scope.$watchCollection(function () {
                    return ServerValidationService.getFormErrorMessage(formTag);
                }, function (value) {
                    if (!!value) {
                        $animate["removeClass"](element, "ng-hide");
                        scope.message = value.message;
                        scope.description = value.description;
                    } else {
                        $animate["addClass"](element, "ng-hide");
                    }
                });
            }
        };
    }]);
});
