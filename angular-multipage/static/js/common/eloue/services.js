"use strict";
define(["../../common/eloue/commonApp", "../../common/eloue/resources", "../../common/eloue/values"],
    function (EloueCommon) {

        /**
         * Service for uploading forms.
         */
        EloueCommon.factory("FormService", [function () {
            var formService = {};

            formService.send = function (method, url, $form, successCallback, errorCallback) {
                $form.ajaxSubmit({
                    type: method,
                    url: url,
                    success: successCallback,
                    error: errorCallback
                });
            };

            return formService;
        }]);

        /**
         * Service for managing users.
         */
        EloueCommon.factory("UsersService", ["Users", "FormService", "Endpoints",
            function (Users, FormService, Endpoints) {
                var usersService = {};

                usersService.get = function (userId, successCallback, errorCallback) {
                    Users.get({id: userId}, successCallback, errorCallback);
                };

                usersService.getMe = function (successCallback, errorCallback) {
                    Users.getMe({_cache: new Date().getTime()}, successCallback, errorCallback);
                };

                usersService.sendForm = function (userId, form, successCallback, errorCallback) {
                    // Calculate current user url
                    var currentUserUrl = Endpoints.api_url + "users/" + userId + "/";

                    // Send form to the current user url
                    FormService.send("POST", currentUserUrl, form, successCallback, errorCallback);
                };

                return usersService;
            }
        ]);
    });