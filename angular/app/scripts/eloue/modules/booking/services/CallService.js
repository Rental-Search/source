define(["angular", "eloue/constants", "eloue/modules/booking/BookingModule"], function (angular) {
    "use strict";
    /**
     * Call service.
     */
    angular.module("EloueApp.BookingModule").factory("CallService", ["$rootScope", "$location", "Endpoints", function ($rootScope, $location, Endpoints) {

        return {

            /**
             * Get phone owner to call product owner.
             * @param ownerId product owner Id
             * @returns Phone number
             */
            getContactCallDetails: function getContactCallDetails(ownerId) {
                //TODO: call real service
                return {
                    "number" : "08.99.45.65.43",
                    "tariff" : "0.15"
                }
            }
        };
    }]);
});
