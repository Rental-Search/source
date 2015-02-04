define(["../../../common/eloue/commonApp", "../../../common/eloue/resources", "../../../common/eloue/values"], function (EloueCommon) {
    "use strict";
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
                        var productDeferred = $q.defer(),
                            productData = {
                                id: value.id,
                                summary: value.summary,
                                deposit_amount: value.deposit_amount
                            },
                            productPromises = {},
                            prices = value.prices;
                        if (prices && prices.length > 0) {
                            angular.forEach(prices, function (price, key) {
                                if (price.unit == 1) {
                                    productData.pricePerDay = price.amount;
                                }
                            });
                        } else {
                            productData.pricePerDay = 0;
                        }
                        if ($.isArray(value.pictures) && (value.pictures.length > 0)) {
                            productData.picture = value.pictures[0].image.thumbnail;
                        }
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
                var deferred = $q.defer(),
                    params = {owner: userId, ordering: "-created_at", _cache: new Date().getTime()};

                if (rootCategoryId) {
                    params.category__isdescendant = rootCategoryId;
                }

                if (page) {
                    params.page = page;
                }

                Products.get(params).$promise.then(function (data) {
                    var promises = [];
                    angular.forEach(data.results, function (value) {
                        var productDeferred = $q.defer(), subPromises = [],
                            product = {
                                id: value.id,
                                summary: value.summary,
                                deposit_amount: value.deposit_amount
                            }, prices = value.prices;

                        if ($.isArray(value.pictures) && (value.pictures.length > 0)) {
                            product.picture = value.pictures[0].image.thumbnail;
                        }

                        if (prices && prices.length > 0) {
                            angular.forEach(prices, function (price, key) {
                                if (price.unit == 1) {
                                    product.pricePerDay = price.amount;
                                }
                            });
                        } else {
                            product.pricePerDay = 0;
                        }

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
                return Products.save(product).$promise;
            };

            productsService.updateProduct = function (product) {
                return Products.update({id: product.id}, product).$promise;
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
                        productPromises.ownerStats = UsersService.getStatistics(productData.owner.id);
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
                return Products.getAbsoluteUrl({id: id, _cache: new Date().getTime()}).$promise;
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

                if (ownerStatsData) {
                    productResult.ownerStats = ownerStatsData;
                }

                return productResult;
            };

            return productsService;
        }
    ]);
});
