define(["angular", "eloue/app", "eloue/resources"], function (angular) {
    "use strict";
    /**
     * User service.
     */
    angular.module("EloueApp").factory("UserService", ["Users", function (Users) {

        return {

            /**
             * Get user by ID.
             * @param userId user ID
             * @returns User
             */
            getUser: function getUser(userId) {
                return Users.get({id: userId});
            }
        };
    }]);
});