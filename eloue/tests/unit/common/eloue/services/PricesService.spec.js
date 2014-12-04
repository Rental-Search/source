define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: PricesService", function () {

        var PricesService,
            pricesMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            pricesMock = {
                getProductPricesPerDay: function () {
                },
                get: function () {
                },
                save: function () {
                },
                update: function () {
                }
            };

            module(function ($provide) {
                $provide.value("Prices", pricesMock);
            });
        });

        beforeEach(inject(function (_PricesService_) {
            PricesService = _PricesService_;
            spyOn(pricesMock, "getProductPricesPerDay").and.callThrough();
            spyOn(pricesMock, "get").and.callThrough();
            spyOn(pricesMock, "save").and.callThrough();
            spyOn(pricesMock, "update").and.callThrough();
        }));

        it("PricesService should be not null", function () {
            expect(!!PricesService).toBe(true);
        });

        it("PricesService:savePrice", function () {
            var price = {id: 1};
            PricesService.savePrice(price);
            expect(pricesMock.save).toHaveBeenCalledWith(price);
        });

        it("PricesService:updatePrice", function () {
            var price = {id: 1};
            PricesService.updatePrice(price);
            expect(pricesMock.update).toHaveBeenCalledWith({id: price.id}, price);
        });
    });
});