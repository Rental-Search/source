define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: MessageThreadsService", function () {

        var MessageThreadsService,
            q,
            messageThreadsMock,
            utilsServiceMock,
            productRelatedMessagesServiceMock,
            productsServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {

            messageThreadsMock = {
                get: function () {
                    return {$promise: {then: function () {
                        return {results: []}
                    }}}
                },
                list: function () {
                    return {$promise: {then: function () {
                        return {results: [
                            {messages: [
                                "http://10.0.0.111:8000/api/2.0/productrelatedmessages/28394/"
                            ]}
                        ]}
                    }}}
                }
            };
            productRelatedMessagesServiceMock = {
                getMessage: function (messageId) {
                },

                getMessageListItem: function (messageId) {
                }
            };
            utilsServiceMock = {
                formatDate: function (date, format) {
                },
                getIdFromUrl: function (url) {
                }
            };
            productsServiceMock = {
                getProduct: function (productId, loadOwner, loadPictures) {
                }
            };

            module(function ($provide) {
                $provide.value("MessageThreads", messageThreadsMock);
                $provide.value("ProductRelatedMessagesService", productRelatedMessagesServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
                $provide.value("ProductsService", productsServiceMock);
            });
        });

        beforeEach(inject(function (_MessageThreadsService_, $q) {
            q = $q;
            MessageThreadsService = _MessageThreadsService_;
            spyOn(messageThreadsMock, "list").and.callThrough();
            spyOn(productRelatedMessagesServiceMock, "getMessage").and.callThrough();
            spyOn(utilsServiceMock, "formatDate").and.callThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").and.callThrough();
            spyOn(productRelatedMessagesServiceMock, "getMessageListItem").and.callThrough();
            spyOn(productsServiceMock, "getProduct").and.callThrough();
        }));

        it("MessageThreadsService should be not null", function () {
            expect(!!MessageThreadsService).toBe(true);
        });

        it("MessageThreadsService:getMessageThread", function () {
            var productId = 1, participantId = 2;
            MessageThreadsService.getMessageThread(productId, participantId);
            expect(messageThreadsMock.list).toHaveBeenCalledWith({product: productId, participant: participantId, _cache: jasmine.any(Number)});
        });

        it("MessageThreadsService:getMessageThreadList", function () {
            var page = 1;
            MessageThreadsService.getMessageThreadList(page);
            expect(messageThreadsMock.get).toHaveBeenCalledWith({page: page, ordering: "-last_message__sent_at", _cache: jasmine.any(Number)});
        });

        it("MessageThreadsService:getMessageThread", function () {
            var threadId = 1;
            MessageThreadsService.getMessageThread(threadId);
            expect(messageThreadsMock.get).toHaveBeenCalledWith({id: threadId, _cache: jasmine.any(Number)});
        });

        it("MessageThreadsService:getUsersRoles", function () {
            var messageThread = {
                sender: {id : 1},
                recipient: {id : 2}
            }, currentUserId = 1;
            var result = MessageThreadsService.getUsersRoles(messageThread, currentUserId);
            expect(result.recipientId).toEqual(messageThread.recipient.id);
        });

        it("MessageThreadsService:parseMessageThreadListItem", function () {
            var messageThreadData = { messages: [{id:1}], last_message: {sent_at: "2014-11-29 12:00:00"}}, lastMessageData = {};
            MessageThreadsService.parseMessageThreadListItem(messageThreadData, lastMessageData);
        });

        it("MessageThreadsService:parseMessageThread", function () {
            var messageThreadData = { messages: [{id:""}]}, messagesDataArray = [], productData = {id: 1};
            MessageThreadsService.parseMessageThread(messageThreadData, messagesDataArray, productData);
        });
    });
});
