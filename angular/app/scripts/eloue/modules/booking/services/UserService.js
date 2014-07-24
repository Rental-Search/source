define(["angular", "eloue/resources", "eloue/modules/booking/BookingModule"], function (angular) {
    "use strict";
    /**
     * User service.
     */
    angular.module("EloueApp.BookingModule").factory("UserService", ["Users", function (Users) {

        return {
            getUser: function getUser(userId) {
                return Users.get({id: userId});
            }
        };
    }]);
});