define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    "use strict";
    /**
     * When the validation error occurred this directive try to find all field with errors by name and add error block.
     * If block contain "eloueFormFieldMessage" with error field name, directive dose not add error block.
     */
    EloueCommon.directive("eloueFormFieldErrorManager", ["$animate", "ServerValidationService", function ($animate, ServerValidationService) {
        var className = "server-validation-error";
        var classInputName = "input-invalid";

        function prepareErrorElement(message) {
            return "<span class='text-danger " + className + "'>" + message + "</span>"
        }

        return {
            restrict: "AE",
            link: function (scope, element, attrs) {
                var formTag = attrs.formTag;
                scope.$watch(function () {
                    return ServerValidationService.getErrors(formTag);
                }, function (value) {
                    var el = element;
                    el.find("." + className).remove();
                    el.find("." + classInputName).removeClass(classInputName);
                    if (!!value) {
                        angular.forEach(value.fields, function (value, key) {
                            var checkItem, input;
                            checkItem = el.find("[field-name='" + key + "']");
                            input = el.find("[name='" + key + "']");
                            input.addClass(classInputName);
                            if (checkItem.length === 0) {
                                input = el.find("[name='" + key + "']");
                                input.parent().append(prepareErrorElement(value));
                            }
                        });
                    }
                });
            }
        };
    }]);
});
