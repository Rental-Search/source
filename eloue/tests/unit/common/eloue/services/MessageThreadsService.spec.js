define(["angular-mocks", "eloue/services/MessageThreadsService"], function () {

    describe("Service: MessageThreadsService", function () {

        var MessageThreadsService,
            q,
            messageThreadsMock,
            utilsServiceMock,
            productRelatedMessagesServiceMock,
            productsServiceMock,
            simpleResourceResponse = {
                $promise: {
                    then: function () {
                        return {results: []};
                    }
                }
            };

        beforeEach(module("EloueCommon"));

        beforeEach(function () {

            messageThreadsMock = {
                get: function () {
                    return simpleResourceResponse;
                },
                list: function () {
                    return simpleResourceResponse;
                }
            };
            productRelatedMessagesServiceMock = {
                getMessage: function (messageId) {
                    return simpleResourceResponse;
                },

                getMessageListItem: function (messageId) {
                    return simpleResourceResponse;
                }
            };
            utilsServiceMock = {
                formatDate: function (date, format) {
                },
                getIdFromUrl: function (url) {
                },
                isToday: function(date) {}
            };
            productsServiceMock = {
                getProduct: function (productId, loadOwner, loadPictures) {
                    return simpleResourceResponse;
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
            spyOn(messageThreadsMock, "get").and.callThrough();
            spyOn(productRelatedMessagesServiceMock, "getMessage").and.callThrough();
            spyOn(utilsServiceMock, "formatDate").and.callThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").and.callThrough();
            spyOn(utilsServiceMock, "isToday").and.callThrough();
            spyOn(productRelatedMessagesServiceMock, "getMessageListItem").and.callThrough();
            spyOn(productsServiceMock, "getProduct").and.callThrough();
        }));

        it("MessageThreadsService should be not null", function () {
            expect(!!MessageThreadsService).toBe(true);
        });

        it("MessageThreadsService:getMessageThreadByProductAndParticipant", function () {
            var productId = 1, participantId = 2;
            MessageThreadsService.getMessageThreadByProductAndParticipant(productId, participantId);
            expect(messageThreadsMock.list).toHaveBeenCalledWith({product: productId, participant: participantId, _cache: jasmine.any(Number)});
        });

        it("MessageThreadsService:getMessageThreadList", function () {
            var page = 1;
            MessageThreadsService.getMessageThreadList(page);
            expect(messageThreadsMock.get).toHaveBeenCalledWith({page: page, ordering: "-last_message__sent_at", _cache: jasmine.any(Number)});
        });

        it("MessageThreadsService:getMessageThreadById", function () {
            var threadId = 1;
            MessageThreadsService.getMessageThreadById(threadId);
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
