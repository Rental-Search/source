define(["angular", "eloue/app", "eloue/resources"], function (angular) {
    "use strict";
    /**
     * User service.
     */
    angular.module("EloueApp").factory("UserService", ["Users", function (Users) {

        return {
            getUser: function getUser(userId) {
                return Users.get({id: userId});
            }
        };
    }]);
});