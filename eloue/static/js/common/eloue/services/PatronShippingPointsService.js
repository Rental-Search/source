define(["../../../common/eloue/commonApp", "../../../common/eloue/resources"], function (EloueCommon) {
    "use strict";
    /**
     * Service for managing patron shipping points.
     */
    EloueCommon.factory("PatronShippingPointsService", [
        "PatronShippingPoints",
        function (PatronShippingPoints) {
            var patronShippingPointsService = {};

            patronShippingPointsService.saveShippingPoint = function (shippingPoint) {
                return PatronShippingPoints.save(shippingPoint).$promise;
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
