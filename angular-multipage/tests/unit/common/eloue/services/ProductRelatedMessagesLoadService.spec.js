define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: ProductRelatedMessagesLoadService", function () {

        var ProductRelatedMessagesLoadService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {

            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_ProductRelatedMessagesLoadService_) {
            ProductRelatedMessagesLoadService = _ProductRelatedMessagesLoadService_;
        }));

        it("ProductRelatedMessagesLoadService should be not null", function () {
            expect(!!ProductRelatedMessagesLoadService).toBe(true);
        });
    });
});
