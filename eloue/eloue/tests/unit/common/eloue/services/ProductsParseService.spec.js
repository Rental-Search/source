define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: ProductsParseService", function () {

        var ProductsParseService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {

            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_ProductsParseService_) {
            ProductsParseService = _ProductsParseService_;
        }));

        it("ProductsParseService should be not null", function () {
            expect(!!ProductsParseService).toBe(true);
        });

        it("ProductsParseService:parseProduct", function () {
            var addressData = {id: 1}, statsData = {id: 5}, ownerData = {id: 2}, ownerStatsData = {id: 4}, phoneData = {id: 3};
            var result = ProductsParseService.parseProduct({}, statsData, addressData, ownerData, ownerStatsData, phoneData, {});
            expect(result).toEqual({stats: statsData, address: addressData, owner: ownerData, ownerStats: ownerStatsData, phone: phoneData});
        });
    });
});