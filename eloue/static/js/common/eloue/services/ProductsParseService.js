"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Service for parsing products.
     */
    EloueCommon.factory("ProductsParseService", [function () {
        var productsParseService = {};

        productsParseService.parseProduct = function (productData, statsData, ownerStatsData) {
            var productResult = angular.copy(productData);

            productResult.stats = statsData;
            if (productResult.stats) {
                if (productResult.stats && productResult.stats.average_rating) {
                    productResult.stats.average_rating = Math.round(productResult.stats.average_rating);
                } else {
                    productResult.stats.average_rating = 0;
                }
            }

            if (!!ownerStatsData) {
                productResult.ownerStats = ownerStatsData;
            }

            return productResult;
        };

        return productsParseService;
    }]);
});
