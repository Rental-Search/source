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
            var statsData = {id: 1}, ownerData = {id: 2}, ownerStatsData = {id: 3};
            var result = ProductsParseService.parseProduct({}, statsData, ownerData, ownerStatsData, {});
            expect(result).toEqual({stats: statsData, owner: ownerData, ownerStats: ownerStatsData});
        });
    });
});