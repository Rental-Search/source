define(["angular", "eloue/constants", "eloue/services", "eloue/modules/booking/BookingModule"], function (angular) {
    "use strict";
    /**
     * Call service.
     */
    angular.module("EloueApp.BookingModule").factory("MessageService", ["$rootScope", "$location", "$q", "Endpoints", "Messages", function ($rootScope, $location, $q, Endpoints, Messages) {

        return {
            getMessageThread: function getMessageThread(productId) {

                    return Messages.list(productId);
            }
        };
    }]);
});
