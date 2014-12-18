define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: ProductsLoadService", function () {

        var ProductsLoadService,
            q,
            productsMock,
            checkAvailabilityMock,
            usersServiceMock,
            productsParseServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            productsMock = {
                get: function () {
                    return {$promise: {then: function () {
                        return {results: []}
                    }}}
                },

                getStats: function () {
                    return {$promise: {}}
                },

                getAbsoluteUrl: function () {
                    return {$promise: {}}
                }
            };
            checkAvailabilityMock = {
                get: function () {
                    return {$promise: {}}
                }
            };
            usersServiceMock = {
                getStatistics: function (userId) {
                    return {$promise: {}}
                }
            };
            productsParseServiceMock = {
                parseProduct: function (productData, statsData, ownerStats) {
                    return {$promise: {}}
                }
            };

            module(function ($provide) {
                $provide.value("Products", productsMock);
                $provide.value("CheckAvailability", checkAvailabilityMock);
                $provide.value("UsersService", usersServiceMock);
                $provide.value("ProductsParseService", productsParseServiceMock);
            });
        });

        beforeEach(inject(function (_ProductsLoadService_, $q) {
            ProductsLoadService = _ProductsLoadService_;
            q = $q;
            spyOn(productsMock, "get").and.callThrough();
            spyOn(productsMock, "getStats").and.callThrough();
            spyOn(productsMock, "getAbsoluteUrl").and.callThrough();
            spyOn(checkAvailabilityMock, "get").and.callThrough();
            spyOn(usersServiceMock, "getStatistics").and.callThrough();
            spyOn(productsParseServiceMock, "parseProduct").and.callThrough();
        }));

        it("ProductsLoadService should be not null", function () {
            expect(!!ProductsLoadService).toBe(true);
        });

        it("ProductsLoadService:getProduct", function () {
            var productId = 1, loadProductStats = true, loadOwnerStats = true;
            ProductsLoadService.getProduct(productId, loadProductStats, loadOwnerStats);
            expect(productsMock.get).toHaveBeenCalledWith({id: productId, _cache: jasmine.any(Number)});
        });

        it("ProductsLoadService:getAbsoluteUrl", function () {
            var id = 1;
            ProductsLoadService.getAbsoluteUrl(id);
            expect(productsMock.getAbsoluteUrl).toHaveBeenCalledWith({id: id, _cache: jasmine.any(Number)});
        });

        it("ProductsLoadService:isAvailable", function () {
            var id = 1, startDate = "2014-11-01 12:00:00", endDate = "2014-11-07 12:00:00", quantity = 1;
            ProductsLoadService.isAvailable(id, startDate, endDate, quantity);
            expect(checkAvailabilityMock.get).toHaveBeenCalledWith({id: id, started_at: startDate, ended_at: endDate, quantity: quantity});
        });
    });
});