define(["../../../common/eloue/commonApp", "../../../common/eloue/resources", "../../../common/eloue/values",
    "../../../common/eloue/services/UtilsService"], function (EloueCommon) {
    "use strict";
    /**
     * Service for managing shippings.
     */
    EloueCommon.factory("ShippingsService", [
        "Shippings",
        "Endpoints",
        "UtilsService",
        function (Shippings, Endpoints, UtilsService) {
            var shippingsService = {};

            shippingsService.getByBooking = function (uuid) {
                return Shippings.get({_cache: new Date().getTime(), booking: uuid}).$promise;
            };

            shippingsService.saveShipping = function (shipping) {
                return Shippings.save(shipping).$promise;
            };

            shippingsService.downloadVoucher = function (id, isOwner) {
                var documentUrl = Endpoints.api_url + "shippings/" + id + "/document/";
                // return shipping document from borrower to owner if current user is owner
                if (isOwner) {
                    documentUrl += "?back=true";
                }
                UtilsService.downloadPdfFile(documentUrl, "voucher.pdf");
            };

            return shippingsService;
        }
    ]);
});
