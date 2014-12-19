"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Service for managing product shipping points.
     */
    EloueCommon.factory("ProductShippingPointsService", [
        "ProductShippingPoints",
        function (ProductShippingPoints) {
            var productShippingPointsService = {};

            productShippingPointsService.saveShippingPoint = function (shippingPoint) {
                return ProductShippingPoints.save(shippingPoint);
            };

            productShippingPointsService.deleteShippingPoint = function (shippingPointId) {
                return ProductShippingPoints.delete({id: shippingPointId});
            };

            productShippingPointsService.getByProduct = function (productId) {
                return ProductShippingPoints.get({_cache: new Date().getTime(), product: productId}).$promise;
            };

            return productShippingPointsService;
        }
    ]);
});
