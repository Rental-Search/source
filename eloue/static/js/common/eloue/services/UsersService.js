"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Service for managing users.
     */
    EloueCommon.factory("UsersService", ["$q", "Users", "FormService", "Endpoints",
        function ($q, Users, FormService, Endpoints) {
            var usersService = {};

            usersService.get = function (userId, successCallback, errorCallback) {
                return Users.get({id: userId, _cache: new Date().getTime()}, successCallback, errorCallback);
            };

            usersService.getMe = function (successCallback, errorCallback) {
                return Users.getMe({_cache: new Date().getTime()}, successCallback, errorCallback);
            };

            usersService.getStatistics = function (userId) {
                return Users.getStats({id: userId, _cache: new Date().getTime()});
            };

            usersService.sendForm = function (userId, form, successCallback, errorCallback) {
                // Calculate current user url
                var currentUserUrl = Endpoints.api_url + "users/" + userId + "/";

                // Send form to the current user url
                FormService.send("PUT", currentUserUrl, form, successCallback, errorCallback);
            };

            usersService.resetPassword = function (userId, form) {
                var resetPasswordUrl = Endpoints.api_url + "users/" + userId + "/reset_password/";
                var deferred = $q.defer();

                FormService.send("POST", resetPasswordUrl, form,
                    function (data) {
                        deferred.resolve(data);
                    },
                    function (reason) {
                        deferred.reject(reason);
                    });

                return deferred.promise;
            };

            usersService.updateUser = function (user) {
                return Users.update({id: "me"}, user);
            };

            return usersService;
        }
    ]);
});
