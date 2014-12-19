"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Service for managing patron shipping points.
     */
    EloueCommon.factory("PatronShippingPointsService", [
        "PatronShippingPoints",
        function (PatronShippingPoints) {
            var patronShippingPointsService = {};

            patronShippingPointsService.saveShippingPoint = function (shippingPoint) {
                return PatronShippingPoints.save(shippingPoint);
            };

            patronShippingPointsService.getByPatronAndBooking = function (userId, bookingId) {
                return PatronShippingPoints.get({
                    _cache: new Date().getTime(),
                    patron: userId,
                    booking: bookingId
                }).$promise;
            };

            return patronShippingPointsService;
        }
    ]);
});
