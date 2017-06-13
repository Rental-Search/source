define(["../../../common/eloue/commonApp", "../../../common/eloue/resources", "../../../common/eloue/values"], function (EloueCommon) {
    "use strict";
    /**
     * Service to store server side validation errors.
     */
    EloueCommon.factory("ServerValidationService", function () {
        var formErrors = {}, rootErrors = "rootErrors",
            serverValidationService = {};

        serverValidationService.addErrors = function (messageError, description, fieldErrors, formTag) {
            if (!formTag) {
                formTag = rootErrors;
            }
            formErrors[formTag] = {
                message: messageError,
                fields: fieldErrors
            };
            if (description) {
                if (angular.isArray(description)) {
                    formErrors[formTag].description = description[0];
                } else {
                    formErrors[formTag].description = description.replace("[", "").replace("]", "").replace("{", "").replace("}", "");
                }
            }
        };
        serverValidationService.removeErrors = function (formTag) {
            if (!formTag) {
                formTag = rootErrors;
            }
            delete formErrors[formTag];
        };
        serverValidationService.getFormErrorMessage = function (formTag) {
            if (!formTag) {
                formTag = rootErrors;
            }
            if ((!formErrors[formTag] || (!formErrors[formTag].message && !formErrors[formTag].description))) {
                return undefined;
            }
            return {message: formErrors[formTag].message, description: formErrors[formTag].description, errors: formErrors[formTag].fields};
        };
        serverValidationService.getFieldError = function (fieldName, formTag) {
            if (!formTag) {
                formTag = rootErrors;
            }
            if (!formErrors[formTag] || !formErrors[formTag].fields) {
                return undefined;
            }
            return formErrors[formTag].fields[fieldName];
        };
        serverValidationService.getErrors = function (formTag) {
            if (!formTag) {
                formTag = rootErrors;
            }
            return formErrors[formTag];
        };
        serverValidationService.addError = function (field, message, formTag) {
            if (!formTag) {
                formTag = rootErrors;
            }
            if (!formErrors[formTag]) {
                formErrors[formTag] = {};
            }
            if (!formErrors[formTag].fields) {
                formErrors[formTag].fields = {};
            }
            formErrors[formTag].fields[field] = message;
        };
        return serverValidationService;
    });
});
