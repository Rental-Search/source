define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: ProductRelatedMessagesParseService", function () {

        var ProductRelatedMessagesParseService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {

            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_ProductRelatedMessagesParseService_) {
            ProductRelatedMessagesParseService = _ProductRelatedMessagesParseService_;
        }));

        it("ProductRelatedMessagesParseService should be not null", function () {
            expect(!!ProductRelatedMessagesParseService).toBe(true);
        });

        it("ProductRelatedMessagesParseService:parseMessage", function () {
            var sender = "Author";
            var result = ProductRelatedMessagesParseService.parseMessage({}, sender);
            expect(result).toEqual({sender: sender});
        });
    });
});
