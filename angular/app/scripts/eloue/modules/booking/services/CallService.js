define(["angular", "eloue/constants", "eloue/services", "eloue/modules/booking/BookingModule"], function (angular) {
    "use strict";
    /**
     * Call service.
     */
    angular.module("EloueApp.BookingModule").factory("CallService", ["$rootScope", "$location", "Endpoints", "Contacts", function ($rootScope, $location, Endpoints, Contacts) {

        return {

            /**
             * Get phone owner to call product owner.
             * @param productId product Id
             * @returns Phone number
             */
            getContactCallDetails: function getContactCallDetails(productId) {
                //TODO: call real service
                return Contacts.get(productId);
            }
        };
    }]);
});
