define(["angular-mocks", "eloue/services/ProductShippingPointsService"], function () {

    describe("Service: ProductShippingPointsService", function () {

        var ProductShippingPointsService,
            productShippingPointsMock,
            simpleResourceResponse = {
                $promise: {
                    then: function () {
                        return {results: []};
                    }
                }
            };

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            productShippingPointsMock = {
                get: function () {
                    return simpleResourceResponse;
                },
                save: function () {
                    return simpleResourceResponse;
                },
                delete: function () {
                    return simpleResourceResponse;
                }
            };
            module(function ($provide) {
                $provide.value("ProductShippingPoints", productShippingPointsMock);
            });
        });

        beforeEach(inject(function (_ProductShippingPointsService_) {
            ProductShippingPointsService = _ProductShippingPointsService_;
            spyOn(productShippingPointsMock, "get").and.callThrough();
            spyOn(productShippingPointsMock, "save").and.callThrough();
            spyOn(productShippingPointsMock, "delete").and.callThrough();
        }));

        it("ProductShippingPointsService should be not null", function () {
            expect(!!ProductShippingPointsService).toBe(true);
        });

        it("ProductShippingPointsService:getById", function () {
            var id = 1;
            ProductShippingPointsService.getById(id);
            expect(productShippingPointsMock.get).toHaveBeenCalledWith({id: id, _cache: jasmine.any(Number)});
        });

        it("ProductShippingPointsService:getByProduct", function () {
            var productId = 1;
            ProductShippingPointsService.getByProduct(productId);
            expect(productShippingPointsMock.get).toHaveBeenCalledWith({_cache: jasmine.any(Number), product: productId});
        });

        it("ProductShippingPointsService:saveShippingPoint", function () {
            var shippingPoint = {};
            ProductShippingPointsService.saveShippingPoint(shippingPoint);
            expect(productShippingPointsMock.save).toHaveBeenCalledWith(shippingPoint);
        });

        it("ProductShippingPointsService:deleteShippingPoint", function () {
            var shippingPointId = 1;
            ProductShippingPointsService.deleteShippingPoint(shippingPointId);
            expect(productShippingPointsMock.delete).toHaveBeenCalledWith({id: shippingPointId});
        });
    });
});
