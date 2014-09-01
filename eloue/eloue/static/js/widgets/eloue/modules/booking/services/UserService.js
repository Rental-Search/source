define(["angular", "../../../../../common/eloue/resources", "eloue/modules/booking/BookingModule"], function (angular) {
    "use strict";
    /**
     * User service.
     */
    angular.module("EloueApp.BookingModule").factory("UserService", ["Users", function (Users) {
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