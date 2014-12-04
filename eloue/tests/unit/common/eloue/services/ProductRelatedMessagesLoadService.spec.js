define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: ProductRelatedMessagesLoadService", function () {

        var ProductRelatedMessagesLoadService,
            productRelatedMessagesMock,
            endpointsMock,
            usersServiceMock,
            utilsServiceMock,
            productRelatedMessagesParseServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            productRelatedMessagesMock = {
                get: function () {
                },
                save: function () {
                }
            };
            endpointsMock = {
            };
            usersServiceMock = {
                get: function (userId) {
                }
            };
            utilsServiceMock = {
                getIdFromUrl: function (url) {
                }
            };
            productRelatedMessagesParseServiceMock = {
                parseMessage: function (messageData, senderData) {
                }
            };

            module(function ($provide) {
                $provide.value("ProductRelatedMessages", productRelatedMessagesMock);
                $provide.value("Endpoints", endpointsMock);
                $provide.value("UsersService", usersServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
                $provide.value("ProductRelatedMessagesParseService", productRelatedMessagesParseServiceMock);
            });
        });

        beforeEach(inject(function (_ProductRelatedMessagesLoadService_) {
            ProductRelatedMessagesLoadService = _ProductRelatedMessagesLoadService_;
            spyOn(productRelatedMessagesMock, "get").and.callThrough();
            spyOn(productRelatedMessagesMock, "save").and.callThrough();
            spyOn(usersServiceMock, "get").and.callThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").and.callThrough();
            spyOn(productRelatedMessagesParseServiceMock, "parseMessage").and.callThrough();
        }));

        it("ProductRelatedMessagesLoadService should be not null", function () {
            expect(!!ProductRelatedMessagesLoadService).toBe(true);
        });
    });
});
