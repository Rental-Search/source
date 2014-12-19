"use strict";
define(["../../../common/eloue/commonApp", "../../../common/eloue/resources"], function (EloueCommon) {
    /**
     * Service for managing product unavailability periods.
     */
    EloueCommon.factory("UnavailabilityPeriodsService", [
        "UnavailabilityPeriods",
        function (UnavailabilityPeriods) {
            var unavailabilityPeriodsService = {};

            unavailabilityPeriodsService.savePeriod = function (period) {
                return UnavailabilityPeriods.save(period);
            };

            unavailabilityPeriodsService.updatePeriod = function (period) {
                return UnavailabilityPeriods.update({id: period.id}, period);
            };

            unavailabilityPeriodsService.deletePeriod = function (period) {
                return UnavailabilityPeriods.delete({id: period.id});
            };

            unavailabilityPeriodsService.getByProduct = function (productId) {
                return UnavailabilityPeriods.get({_cache: new Date().getTime(), product: productId}).$promise;
            };

            return unavailabilityPeriodsService;
        }
    ]);
});
