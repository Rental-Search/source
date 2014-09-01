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
            spyOn(productRelatedMessagesMock, "get").andCallThrough();
            spyOn(productRelatedMessagesMock, "save").andCallThrough();
            spyOn(usersServiceMock, "get").andCallThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").andCallThrough();
            spyOn(productRelatedMessagesParseServiceMock, "parseMessage").andCallThrough();
        }));

        it("ProductRelatedMessagesLoadService should be not null", function () {
            expect(!!ProductRelatedMessagesLoadService).toBe(true);
        });
    });
});
