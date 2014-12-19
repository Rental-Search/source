"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Service to store server side validation errors.
     */
    EloueCommon.factory("ServerValidationService", function () {
        var formErrors = {}, rootErrors = "rootErrors";

        return {
            addErrors: function (messageError, description, fieldErrors, formTag) {
                if (!formTag) {
                    formTag = rootErrors;
                }
                formErrors[formTag] = {
                    message: messageError,
                    fields: fieldErrors
                };
                if (!!description) {
                    formErrors[formTag].description = ("" + description).replace("[", "").replace("]", "").replace("{", "").replace("}", "");
                }
            },
            removeErrors: function (formTag) {
                if (!formTag) {
                    formTag = rootErrors;
                }
                delete formErrors[formTag];
            },
            getFormErrorMessage: function (formTag) {
                if (!formTag) {
                    formTag = rootErrors;
                }
                if ((!formErrors[formTag] || (!formErrors[formTag].message && !formErrors[formTag].description))) {
                    return undefined;
                }
                return {message: formErrors[formTag].message, description: formErrors[formTag].description};
            },
            getFieldError: function (fieldName, formTag) {
                if (!formTag) {
                    formTag = rootErrors;
                }
                if (!formErrors[formTag] || !formErrors[formTag].fields) {
                    return undefined;
                }
                return formErrors[formTag].fields[fieldName];
            },
            getErrors: function (formTag) {
                if (!formTag) {
                    formTag = rootErrors;
                }
                return formErrors[formTag];
            },
            addError: function (field, message, formTag) {
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
            }
        };
    });
});
