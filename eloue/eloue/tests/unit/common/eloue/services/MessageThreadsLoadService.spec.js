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
                getProduct: function (productId, loadAddress, loadOwner, loadPhone, loadPictures) {
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
            spyOn(messageThreadsMock, "get").andCallThrough();
            spyOn(usersServiceMock, "get").andCallThrough();
            spyOn(productRelatedMessagesServiceMock, "getMessage").andCallThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").andCallThrough();
            spyOn(messageThreadsParseServiceMock, "parseMessageThread").andCallThrough();
            spyOn(productRelatedMessagesLoadServiceMock, "getMessageListItem").andCallThrough();
            spyOn(productsLoadServiceMock, "getProduct").andCallThrough();
        }));

        it("MessageThreadsLoadService should be not null", function () {
            expect(!!MessageThreadsLoadService).toBe(true);
        });
    });
});