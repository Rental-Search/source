"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Service for managing products.
     */
    EloueCommon.factory("ProductsLoadService", [
        "$q",
        "Products",
        "CheckAvailability",
        "UsersService",
        "ProductsParseService",
        function ($q, Products, CheckAvailability, UsersService, ProductsParseService) {
            var productsLoadService = {};

            productsLoadService.getProduct = function (productId, loadProductStats, loadOwnerStats) {
                var deferred = $q.defer();

                // Load product
                Products.get({id: productId, _cache: new Date().getTime()}).$promise.then(function (productData) {
                    var productPromises = {};

                    if (loadProductStats) {
                        productPromises.stats = Products.getStats({id: productId, _cache: new Date().getTime()});
                    }
                    if (loadOwnerStats) {
                        productPromises.ownerStats = UsersService.getStatistics(productData.owner.id).$promise;
                    }
                    // When all data loaded
                    $q.all(productPromises).then(function (results) {
                        var product = ProductsParseService.parseProduct(productData, results.stats, results.ownerStats);
                        deferred.resolve(product);
                    });
                });

                return deferred.promise;
            };

            productsLoadService.getAbsoluteUrl = function (id) {
                return Products.getAbsoluteUrl({id: id, _cache: new Date().getTime()});
            };

            productsLoadService.isAvailable = function (id, startDate, endDate, quantity) {
                return CheckAvailability.get({
                    id: id,
                    started_at: startDate,
                    ended_at: endDate,
                    quantity: quantity
                }).$promise;
            };

            return productsLoadService;
        }
    ]);
});
