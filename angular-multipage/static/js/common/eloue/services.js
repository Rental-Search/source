"use strict";
define(["../../common/eloue/commonApp", "../../common/eloue/resources", "../../common/eloue/values"],
    function (EloueCommon) {

        /**
         * Service for uploading forms.
         */
        EloueCommon.factory("FormDataService", [function () {
            var formDataService = {};

            formDataService.send = function (action, textFields, fileFields, completeCallback) {
                $.ajax(action, {
                    data: textFields.serializeArray(),
                    files: fileFields,
                    iframe: true,
                    processData: false
                }).complete(function (data) {
                    if (!!completeCallback) {
                        completeCallback(data);
                    }
                });
            };

            return formDataService;
        }]);

        /**
         * Service for managing users.
         */
        EloueCommon.factory("UsersService", ["Users", "FormDataService", "Endpoints",
            function (Users, FormDataService, Endpoints) {
                var usersService = {};

                usersService.get = function (userId, successCallback, errorCallback) {
                    Users.get({id: userId}, successCallback, errorCallback);
                };

                usersService.getMe = function (successCallback, errorCallback) {
                    Users.getMe({}, successCallback, errorCallback);
                };

                usersService.sendFormData = function (userId, textFields, fileFields, completeCallback) {
                    var currentUserUrl = Endpoints.api_url + "users/" + userId + "/";

                    FormDataService.send(currentUserUrl, textFields, fileFields, completeCallback);
                };

                return usersService;
            }
        ]);
    });