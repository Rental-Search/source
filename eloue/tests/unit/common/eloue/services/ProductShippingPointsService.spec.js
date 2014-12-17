define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: ProductShippingPointsService", function () {

        var ProductShippingPointsService,
            productShippingPointsMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            productShippingPointsMock = {
                get: function () {
                    return {$promise: {}}
                },
                save: function () {
                    return {$promise: {}}
                },
                delete: function () {
                    return {$promise: {}}
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
