define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: ProductsLoadService", function () {

        var ProductsLoadService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_ProductsLoadService_) {
            ProductsLoadService = _ProductsLoadService_;
        }));

        it("ProductsLoadService should be not null", function () {
            expect(!!ProductsLoadService).toBe(true);
        });
    });
});