"use strict";
define(["../../common/eloue/commonApp"], function (EloueCommon) {

    /**
     * Controller for the login form.
     */
    EloueCommon.factory("ErrorHandlerInterceptor", ["$timeout", "$q", function ($timeout, $q) {
        var elementsList = $();

        // this message will appear for a defined amount of time and then vanish again
        var showMessage = function(content, cl, time) {
            console.log(content);

        };
        return function (promise) {
            return promise.then(function (successResponse) {
                    return successResponse;
                },
                // if the message returns unsuccessful we display the error
                function (errorResponse) {
                    console.log(errorResponse);
                    switch (errorResponse.status) {
                        case 400: // if the status is 400 we return the error
                            showMessage("Bad request", 'xx-http-error-message', 6000);
                            // if we have found validation error messages we will loop through
                            // and display them

                            break;
                        case 401: // if the status is 401 we return access denied
                            showMessage('You are unauthorised to view this page!',
                                'xx-http-error-message', 6000);
                            break;
                        case 403: // if the status is 403 we tell the user that authorization was denied
                            showMessage('You don\'t have enough rights to view this page!',
                                'xx-http-error-message', 6000);
                            break;
                        case 500: // if the status is 500 we return an internal server error message
                            showMessage('Internal server error occurred',
                                'xx-http-error-message', 6000);
                            break;
                        default: // for all other errors we display a default error message
                            showMessage('Unexpected error occurred',
                                'xx-http-error-message', 6000);
                    }
                    return $q.reject(errorResponse.data);
                });
        };
    }]);
});