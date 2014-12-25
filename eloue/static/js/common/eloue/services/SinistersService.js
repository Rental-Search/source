define(["../../../common/eloue/commonApp", "../../../common/eloue/resources"], function (EloueCommon) {
    "use strict";
    /**
     * Service for managing sinisters.
     */
    EloueCommon.factory("SinistersService", [
        "Sinisters",
        function (Sinisters) {
            var sinistersService = {};

            sinistersService.getSinisterList = function (bookingUUID) {
                return Sinisters.get({_cache: new Date().getTime(), booking: bookingUUID}).$promise;
            };

            return sinistersService;
        }
    ]);
});
