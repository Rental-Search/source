define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: ProductRelatedMessagesService", function () {

        var ProductRelatedMessagesService,
            productRelatedMessagesMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            productRelatedMessagesMock = {
                get: function () {
                }
            };

            module(function ($provide) {
                $provide.value("ProductRelatedMessages", productRelatedMessagesMock);
            });
        });

        beforeEach(inject(function (_ProductRelatedMessagesService_) {
            ProductRelatedMessagesService = _ProductRelatedMessagesService_;
            spyOn(productRelatedMessagesMock, "get").and.callThrough();
        }));

        it("ProductRelatedMessagesService should be not null", function () {
            expect(!!ProductRelatedMessagesService).toBe(true);
        });

        it("ProductRelatedMessagesService:getMessage", function () {
            var messageId = 1;
            ProductRelatedMessagesService.getMessage(messageId);
            expect(productRelatedMessagesMock.get).toHaveBeenCalledWith({id: messageId, _cache: jasmine.any(Number)});
        });
    });
});
