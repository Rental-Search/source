define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: ProductRelatedMessagesService", function () {

        var ProductRelatedMessagesService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {

            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_ProductRelatedMessagesService_) {
            ProductRelatedMessagesService = _ProductRelatedMessagesService_;
        }));

        it("ProductRelatedMessagesService should be not null", function () {
            expect(!!ProductRelatedMessagesService).toBe(true);
        });
    });
});
