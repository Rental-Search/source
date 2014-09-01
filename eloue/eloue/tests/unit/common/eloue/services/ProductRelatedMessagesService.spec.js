define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: ProductRelatedMessagesService", function () {

        var ProductRelatedMessagesService,
            productRelatedMessagesMock,
            endpointsMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            productRelatedMessagesMock = {
                get: function () {
                },
                save: function () {
                }
            };
            endpointsMock = {};

            module(function ($provide) {
                $provide.value("ProductRelatedMessages", productRelatedMessagesMock);
                $provide.value("Endpoints", endpointsMock);
            });
        });

        beforeEach(inject(function (_ProductRelatedMessagesService_) {
            ProductRelatedMessagesService = _ProductRelatedMessagesService_;
            spyOn(productRelatedMessagesMock, "get").andCallThrough();
            spyOn(productRelatedMessagesMock, "save").andCallThrough();
        }));

        it("ProductRelatedMessagesService should be not null", function () {
            expect(!!ProductRelatedMessagesService).toBe(true);
        });
    });
});
