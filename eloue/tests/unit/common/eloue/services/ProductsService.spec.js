define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: ProductsService", function () {

        var ProductsService,
            q,
            productsMock,
            productsParseServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            productsMock = {
                get: function () {
                    return {$promise: {then: function () {
                        return {results: []}
                    }}}
                },
                update: function (id, product) {

                },
                save: function(product) {}
            };
            productsParseServiceMock = {
                parseProduct: function(productData, stats, ownerStats) {}
            };

            module(function ($provide) {
                $provide.value("Products", productsMock);
                $provide.value("ProductsParseService", productsParseServiceMock);
            });
        });

        beforeEach(inject(function (_ProductsService_, $q) {
            ProductsService = _ProductsService_;
            q = $q;
            spyOn(productsMock, "get").and.callThrough();
            spyOn(productsMock, "save").and.callThrough();
            spyOn(productsMock, "update").and.callThrough();
            spyOn(productsParseServiceMock, "parseProduct").and.callThrough();
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
    });
});