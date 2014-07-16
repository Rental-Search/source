define(["angular", "eloue/constants", "eloue/services", "eloue/modules/booking/BookingModule"], function (angular) {
    "use strict";
    /**
     * Call service.
     */
    angular.module("EloueApp.BookingModule").factory("MessageService", ["$rootScope", "$location", "Endpoints", "Messages", function ($rootScope, $location, Endpoints, Messages) {

        return {
            getMessageThread: function getMessageThread(productId) {

                var messageThread = Messages.list();
                console.log(messageThread.messages);
                return messageThread.messages;

            }
        };
    }]);
});
