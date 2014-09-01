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
    });
});