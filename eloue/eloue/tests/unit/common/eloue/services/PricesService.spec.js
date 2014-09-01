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
    });
});