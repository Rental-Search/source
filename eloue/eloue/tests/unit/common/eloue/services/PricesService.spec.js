define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: PricesService", function () {

        var PricesService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_PricesService_) {
            PricesService = _PricesService_;
        }));

        it("PricesService should be not null", function () {
            expect(!!PricesService).toBe(true);
        });
    });
});