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
            var statsData = {id: 1}, ownerStatsData = {id: 3};
            var result = ProductsParseService.parseProduct({}, statsData, ownerStatsData, {});
            expect(result).toEqual({stats: statsData, ownerStats: ownerStatsData});
        });
    });
});