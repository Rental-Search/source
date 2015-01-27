define(["../../../common/eloue/commonApp", "../../../common/eloue/resources"], function (EloueCommon) {
    "use strict";
    /**
     * Service for managing product shipping points.
     */
    EloueCommon.factory("ProductShippingPointsService", [
        "ProductShippingPoints",
        function (ProductShippingPoints) {
            var productShippingPointsService = {};

            productShippingPointsService.saveShippingPoint = function (shippingPoint) {
                return ProductShippingPoints.save(shippingPoint).$promise;
            };

            productShippingPointsService.deleteShippingPoint = function (shippingPointId) {
                return ProductShippingPoints.delete({id: shippingPointId}).$promise;
            };

            productShippingPointsService.getByProduct = function (productId) {
                return ProductShippingPoints.get({_cache: new Date().getTime(), product: productId}).$promise;
            };

            productShippingPointsService.getById = function (id) {
                return ProductShippingPoints.get({
                    id: id,
                    _cache: new Date().getTime()
                }).$promise;
            };

            return productShippingPointsService;
        }
    ]);
});
