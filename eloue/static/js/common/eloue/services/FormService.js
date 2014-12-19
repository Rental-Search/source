"use strict";
define(["../../../common/eloue/commonApp", "../../../common/eloue/resources", "../../../common/eloue/values",
    "../../../common/eloue/services/ServerValidationService"], function (EloueCommon) {
    /**
     * Service for uploading forms.
     */
    EloueCommon.factory("FormService", ["ServerValidationService", function (ServerValidationService) {
        var formService = {};

        formService.send = function (method, url, $form, successCallback, errorCallback) {
            ServerValidationService.removeErrors();
            $form.ajaxSubmit({
                type: method,
                url: url,
                success: successCallback,
                error: function (jqXHR, status, message, form) {
                    if (jqXHR.status == 400 && !!jqXHR.responseJSON) {
                        ServerValidationService.addErrors(jqXHR.responseJSON.message, jqXHR.description, jqXHR.responseJSON.errors);
                    } else {
                        ServerValidationService.addErrors("An error occured!", "An error occured!");
                    }
                    errorCallback.call(null, jqXHR, status, message, form);
                }
            });
        };

        return formService;
    }]);
});
