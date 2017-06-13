define(["angular-mocks", "eloue/services/ProductsService"], function () {

    describe("Service: ProductsService", function () {

        var ProductsService,
            q,
            productsMock,
            checkAvailabilityMock,
            usersServiceMock,
            simpleResourceResponse = {
                $promise: {
                    then: function () {
                        return {results: []};
                    }
                }
            };

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            productsMock = {
                get: function () {
                    return simpleResourceResponse;
                },
                update: function (id, product) {
                    return simpleResourceResponse;
                },
                save: function(product) {
                    return simpleResourceResponse;
                },

                getStats: function () {
                    return simpleResourceResponse;
                },

                getAbsoluteUrl: function () {
                    return simpleResourceResponse;
                }
            };
            checkAvailabilityMock = {
                get: function () {
                    return simpleResourceResponse;
                }
            };
            usersServiceMock = {
                getStatistics: function (userId) {
                    return simpleResourceResponse;
                }
            };

            module(function ($provide) {
                $provide.value("Products", productsMock);
                $provide.value("CheckAvailability", checkAvailabilityMock);
                $provide.value("UsersService", usersServiceMock);
            });
        });

        beforeEach(inject(function (_ProductsService_, $q) {
            ProductsService = _ProductsService_;
            q = $q;
            spyOn(productsMock, "get").and.callThrough();
            spyOn(productsMock, "save").and.callThrough();
            spyOn(productsMock, "update").and.callThrough();
            spyOn(productsMock, "getStats").and.callThrough();
            spyOn(productsMock, "getAbsoluteUrl").and.callThrough();
            spyOn(checkAvailabilityMock, "get").and.callThrough();
            spyOn(usersServiceMock, "getStatistics").and.callThrough();
        }));

        it("ProductsService should be not null", function () {
            expect(!!ProductsService).toBe(true);
        });

        it("ProductsService:getProductDetails", function () {
            var id = 1;
            ProductsService.getProductDetails(id);
            expect(productsMock.get).toHaveBeenCalledWith({id: id, _cache: jasmine.any(Number)});
        });

        it("ProductsService:getProductsByAddress", function () {
            var addressId = 2;
            ProductsService.getProductsByAddress(addressId);
            expect(productsMock.get).toHaveBeenCalledWith({address: addressId, _cache: jasmine.any(Number)});
        });

        it("ProductsService:getProductsByOwnerAndRootCategory", function () {
            var userId = 1, rootCategoryId = 2, page = 3;
            ProductsService.getProductsByOwnerAndRootCategory(userId, rootCategoryId, page);
            expect(productsMock.get).toHaveBeenCalledWith({owner: userId, ordering: "-created_at", _cache: jasmine.any(Number), category__isdescendant: rootCategoryId, page: page});
        });

        it("ProductsService:saveProduct", function () {
            var product = {id: 2};
            ProductsService.saveProduct(product);
            expect(productsMock.save).toHaveBeenCalledWith(product);
        });

        it("ProductsService:updateProduct", function () {
            var product = {id: 2};
            ProductsService.updateProduct(product);
            expect(productsMock.update).toHaveBeenCalledWith({id: product.id}, product);
        });

        it("ProductsService:getProduct", function () {
            var productId = 1, loadProductStats = true, loadOwnerStats = true;
            ProductsService.getProduct(productId, loadProductStats, loadOwnerStats);
            expect(productsMock.get).toHaveBeenCalledWith({id: productId, _cache: jasmine.any(Number)});
        });

        it("ProductsService:getAbsoluteUrl", function () {
            var id = 1;
            ProductsService.getAbsoluteUrl(id);
            expect(productsMock.getAbsoluteUrl).toHaveBeenCalledWith({id: id, _cache: jasmine.any(Number)});
        });

        it("ProductsService:isAvailable", function () {
            var id = 1, startDate = "2014-11-01 12:00:00", endDate = "2014-11-07 12:00:00", quantity = 1;
            ProductsService.isAvailable(id, startDate, endDate, quantity);
            expect(checkAvailabilityMock.get).toHaveBeenCalledWith({id: id, started_at: startDate, ended_at: endDate, quantity: quantity});
        });

        it("ProductsService:parseProduct", function () {
            var statsData = {id: 1}, ownerStatsData = {id: 3};
            var result = ProductsService.parseProduct({}, statsData, ownerStatsData);
            expect(result).toEqual({stats: statsData, ownerStats: ownerStatsData});
        });
    });
});