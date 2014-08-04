"use strict";
define(["../../common/eloue/commonApp", "../../common/eloue/resources"], function (EloueCommon) {

    /**
     * Service for managing users.
     */
    EloueCommon.factory("UsersService", ["Users", function (Users) {
        var usersService = {};

        usersService.get = function (userId, successCallback, errorCallback) {
            Users.get({id: userId}, successCallback, errorCallback);
        };

        usersService.getMe = function (successCallback, errorCallback) {
            Users.getMe({}, successCallback, errorCallback);
        };

        return usersService;
    }]);
});