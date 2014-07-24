define(["angular", "eloue/constants", "eloue/resources", "eloue/modules/booking/BookingModule"], function (angular) {
    "use strict";
    /**
     * Call service.
     */
    angular.module("EloueApp.BookingModule").factory("MessageService", ["$q", "Endpoints", "Messages", function ($q, Endpoints, Messages) {

        return {
            getMessageThread: function getMessageThread(productId) {
                return Messages.list({product: productId});
            }
        };
    }]);
});
