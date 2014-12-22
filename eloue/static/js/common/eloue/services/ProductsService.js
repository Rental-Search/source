"use strict";
define(["../../../common/eloue/commonApp", "../../../common/eloue/resources", "../../../common/eloue/values"], function (EloueCommon) {
    /**
     * Service for managing products.
     */
    EloueCommon.factory("ProductsService", [
        "$q",
        "Products",
        "CheckAvailability",
        "UsersService",
        function ($q, Products, CheckAvailability, UsersService) {
            var productsService = {};

            productsService.getProductDetails = function (id) {
                return Products.get({id: id, _cache: new Date().getTime()}).$promise;
            };

            productsService.getProductsByAddress = function (addressId) {
                var deferred = $q.defer();

                Products.get({address: addressId, _cache: new Date().getTime()}).$promise.then(function (data) {
                    var promises = [];

                    angular.forEach(data.results, function (value, key) {
                        var productDeferred = $q.defer();

                        var productData = {
                            id: value.id,
                            summary: value.summary,
                            deposit_amount: value.deposit_amount
                        };

                        var productPromises = {};
                        productPromises.stats = Products.getStats({id: value.id, _cache: new Date().getTime()});

                        // When all data loaded
                        $q.all(productPromises).then(function (results) {
                            var product = productsService.parseProduct(productData, results.stats, results.ownerStats);
                            productDeferred.resolve(product);
                        });

                        promises.push(productDeferred.promise);
                    });

                    $q.all(promises).then(
                        function (results) {
                            deferred.resolve(results);
                        },
                        function (reasons) {
                            deferred.reject(reasons);
                        }
                    );
                });

                return deferred.promise;
            };

            productsService.getProductsByOwnerAndRootCategory = function (userId, rootCategoryId, page) {
                var deferred = $q.defer();
                var params = {owner: userId, ordering: "-created_at", _cache: new Date().getTime()};

                if (rootCategoryId) {
                    params.category__isdescendant = rootCategoryId;
                }

                if (page) {
                    params.page = page;
                }

                Products.get(params).$promise.then(function (data) {
                    var promises = [];
                    angular.forEach(data.results, function (value, key) {
                        var productDeferred = $q.defer();

                        var product = {
                            id: value.id,
                            summary: value.summary,
                            deposit_amount: value.deposit_amount
                        };

                        if ($.isArray(value.pictures) && (value.pictures.length > 0)) {
                            product.picture = value.pictures[0].image.thumbnail;
                        }

                        if (value.prices && value.prices.length > 0) {
                            product.pricePerDay = value.prices[0].amount;
                        } else {
                            product.pricePerDay = 0;
                        }

                        var subPromises = [];
                        subPromises.push(Products.getStats({
                            id: product.id,
                            _cache: new Date().getTime()
                        }).$promise);
                        $q.all(subPromises).then(
                            function (results) {
                                product.stats = results[0];
                                if (product.stats) {
                                    if (product.stats.average_rating) {
                                        product.stats.average_rating = Math.round(product.stats.average_rating);
                                    } else {
                                        product.stats.average_rating = 0;
                                    }
                                }
                                productDeferred.resolve(product);
                            },
                            function (reasons) {
                                productDeferred.reject(reasons);
                            }
                        );

                        promises.push(productDeferred.promise);
                    });

                    $q.all(promises).then(
                        function (results) {
                            deferred.resolve({
                                list: results,
                                next: data.next
                            });
                        },
                        function (reasons) {
                            deferred.reject(reasons);
                        }
                    );
                });

                return deferred.promise;
            };

            productsService.saveProduct = function (product) {
                return Products.save(product);
            };

            productsService.updateProduct = function (product) {
                return Products.update({id: product.id}, product);
            };

            productsService.getProduct = function (productId, loadProductStats, loadOwnerStats) {
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
                        var product = productsService.parseProduct(productData, results.stats, results.ownerStats);
                        deferred.resolve(product);
                    });
                });

                return deferred.promise;
            };

            productsService.getAbsoluteUrl = function (id) {
                return Products.getAbsoluteUrl({id: id, _cache: new Date().getTime()});
            };

            productsService.isAvailable = function (id, startDate, endDate, quantity) {
                return CheckAvailability.get({
                    id: id,
                    started_at: startDate,
                    ended_at: endDate,
                    quantity: quantity
                }).$promise;
            };

            productsService.parseProduct = function (productData, statsData, ownerStatsData) {
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

            return productsService;
        }
    ]);
});
