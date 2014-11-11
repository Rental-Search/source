"use strict";
define(["../../common/eloue/commonApp", "toastr"], function (EloueCommon, toastr) {

    /**
     * Generic error handler interceptor.
     */
    EloueCommon.factory("ErrorHandlerInterceptor", ["$q", "$rootScope", "ServerValidationService", function ($q, $rootScope, ServerValidationService) {

        // this message will appear for a defined amount of time and then vanish again
        var showMessage = function (content) {
            toastr.options.positionClass = "toast-top-full-width";
            toastr.error(content, "Error!");
        };

        return {
            'request': function (config) {
                if (!!config.data && !!config.data.formTag) {
                    var formTag = config.data.formTag, resultConfig;
                    // copy config to not change object in controllers.
                    resultConfig = angular.copy(config);
                    // remove formTag from request body.
                    delete resultConfig.data.formTag;
                    // put formTag in request config.
                    resultConfig.formTag = formTag;

                    ServerValidationService.removeErrors(formTag);
                    return $q.when(resultConfig);
                } else {
                    return $q.when(config);
                }
            },
            'responseError': function (errorResponse) {
                // if the message returns unsuccessful we display the error
                switch (errorResponse.status) {
                    case 400:
                        if (!!errorResponse.config && !!errorResponse.data && !!errorResponse.config.formTag) {
                            ServerValidationService.addErrors(errorResponse.config.formTag,
                                errorResponse.data.message,
                                errorResponse.data.errors);
                        }
//                            showMessage("A required attribute of the API request is missing");
                        break;
                    case 401:
                        $rootScope.$broadcast("redirectToLogin");
                        break;
                    case 403:
                        showMessage("The request is not allowed");
                        break;
                    case 404:
                        showMessage("A resource could not be accessed");
                        break;
                    case 405:
                        showMessage("The request is not supported");
                        break;
                    case 500:
                        showMessage("While handling the request something went wrong on the server side");
                        break;
                    default:
                        showMessage("Unexpected error");
                }
                return $q.reject(errorResponse.data);
            }
        };
    }]);

});