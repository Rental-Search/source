define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: MessageThreadsLoadService", function () {

        var MessageThreadsLoadService,
            q,
            messageThreadsMock,
            utilsServiceMock,
            messageThreadsParseServiceMock,
            productRelatedMessagesLoadServiceMock,
            productsLoadServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            messageThreadsMock = {
                get: function () {
                    return {$promise: {then: function () {
                        return {results: []}
                    }}}
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
                $provide.value("UtilsService", utilsServiceMock);
                $provide.value("MessageThreadsParseService", messageThreadsParseServiceMock);
                $provide.value("ProductRelatedMessagesLoadService", productRelatedMessagesLoadServiceMock);
                $provide.value("ProductsLoadService", productsLoadServiceMock);
            });
        });

        beforeEach(inject(function (_MessageThreadsLoadService_, $q) {
            MessageThreadsLoadService = _MessageThreadsLoadService_;
            q = $q;
            spyOn(messageThreadsMock, "get").and.callThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").and.callThrough();
            spyOn(messageThreadsParseServiceMock, "parseMessageThread").and.callThrough();
            spyOn(productRelatedMessagesLoadServiceMock, "getMessageListItem").and.callThrough();
            spyOn(productsLoadServiceMock, "getProduct").and.callThrough();
        }));

        it("MessageThreadsLoadService should be not null", function () {
            expect(!!MessageThreadsLoadService).toBe(true);
        });

        it("MessageThreadsLoadService:getMessageThreadList", function () {
            var page = 1;
            MessageThreadsLoadService.getMessageThreadList(page);
        });

        it("MessageThreadsLoadService:getMessageThread", function () {
            var threadId = 1;
            MessageThreadsLoadService.getMessageThread(threadId);
        });

        it("MessageThreadsLoadService:getUsersRoles", function () {
            var messageThread = {
                sender: {id : 1},
                recipient: {id : 2}
            }, currentUserId = 1;
            MessageThreadsLoadService.getUsersRoles(messageThread, currentUserId);
        });
    });
});