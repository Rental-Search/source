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
            var addressData = {id: 1}, ownerData = {id: 2}, phoneData = {id: 3};
            var result = ProductsParseService.parseProduct({}, addressData, ownerData, phoneData, {});
            expect(result).toEqual({address: addressData, owner: ownerData, phone: phoneData});
        });
    });
});