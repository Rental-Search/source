define(["../../../common/eloue/commonApp", "../../../common/eloue/resources"], function (EloueCommon) {
    "use strict";
    /**
     * Service for managing product unavailability periods.
     */
    EloueCommon.factory("UnavailabilityPeriodsService", [
        "UnavailabilityPeriods",
        function (UnavailabilityPeriods) {
            var unavailabilityPeriodsService = {};

            unavailabilityPeriodsService.savePeriod = function (period) {
                return UnavailabilityPeriods.save(period).$promise;
            };

            unavailabilityPeriodsService.updatePeriod = function (period) {
                return UnavailabilityPeriods.update({id: period.id}, period).$promise;
            };

            unavailabilityPeriodsService.deletePeriod = function (period) {
                return UnavailabilityPeriods.delete({id: period.id}).$promise;
            };

            unavailabilityPeriodsService.getByProduct = function (productId) {
                return UnavailabilityPeriods.get({_cache: new Date().getTime(), product: productId}).$promise;
            };

            return unavailabilityPeriodsService;
        }
    ]);
});
