define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: MessageThreadsLoadService", function () {

        var MessageThreadsLoadService,
            messageThreadsMock,
            usersServiceMock,
            productRelatedMessagesServiceMock,
            utilsServiceMock,
            messageThreadsParseServiceMock,
            productRelatedMessagesLoadServiceMock,
            productsLoadServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            messageThreadsMock = {
                get: function () {
                }
            };
            usersServiceMock = {
                get: function (userId) {
                }
            };
            productRelatedMessagesServiceMock = {
                getMessage: function (messageId) {
                }
            };
            utilsServiceMock = {
                getIdFromUrl: function (url) {
                }
            };
            messageThreadsParseServiceMock = {
                parseMessageThread: function (messageThreadData, messages, product) {
                }
            };
            productRelatedMessagesLoadServiceMock = {
                getMessageListItem: function (messageId) {
                }
            };
            productsLoadServiceMock = {
                getProduct: function (productId, loadOwner, loadPictures) {
                }
            };

            module(function ($provide) {
                $provide.value("MessageThreads", messageThreadsMock);
                $provide.value("UsersService", usersServiceMock);
                $provide.value("ProductRelatedMessagesService", productRelatedMessagesServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
                $provide.value("MessageThreadsParseService", messageThreadsParseServiceMock);
                $provide.value("ProductRelatedMessagesLoadService", productRelatedMessagesLoadServiceMock);
                $provide.value("ProductsLoadService", productsLoadServiceMock);
            });
        });

        beforeEach(inject(function (_MessageThreadsLoadService_) {
            MessageThreadsLoadService = _MessageThreadsLoadService_;
            spyOn(messageThreadsMock, "get").and.callThrough();
            spyOn(usersServiceMock, "get").and.callThrough();
            spyOn(productRelatedMessagesServiceMock, "getMessage").and.callThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").and.callThrough();
            spyOn(messageThreadsParseServiceMock, "parseMessageThread").and.callThrough();
            spyOn(productRelatedMessagesLoadServiceMock, "getMessageListItem").and.callThrough();
            spyOn(productsLoadServiceMock, "getProduct").and.callThrough();
        }));

        it("MessageThreadsLoadService should be not null", function () {
            expect(!!MessageThreadsLoadService).toBe(true);
        });
    });
});