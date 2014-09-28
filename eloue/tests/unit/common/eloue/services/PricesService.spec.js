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
            spyOn(pricesMock, "getProductPricesPerDay").andCallThrough();
            spyOn(pricesMock, "get").andCallThrough();
            spyOn(pricesMock, "save").andCallThrough();
            spyOn(pricesMock, "update").andCallThrough();
        }));

        it("PricesService should be not null", function () {
            expect(!!PricesService).toBe(true);
        });

        it("PricesService:getProductPricesPerDay", function () {
            var productId = 1;
            PricesService.getProductPricesPerDay(productId);
            expect(pricesMock.getProductPricesPerDay).toHaveBeenCalledWith({product: productId});
        });

        it("PricesService:getPricesByProduct:", function () {
            var productId = 1;
            PricesService.getPricesByProduct(productId);
            expect(pricesMock.get).toHaveBeenCalledWith({product: productId});
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