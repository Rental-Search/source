define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: ProductRelatedMessagesLoadService", function () {

        var ProductRelatedMessagesLoadService,
            q,
            productRelatedMessagesMock,
            endpointsMock,
            messageThreadsMock,
            usersServiceMock,
            utilsServiceMock,
            productRelatedMessagesParseServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            productRelatedMessagesMock = {
                get: function () {
                    return {$promise: {then: function () {
                        return {results: []}
                    }}}
                },
                save: function () {
                    return {$promise: {then: function () {
                        return {results: []}
                    }}}
                },
                update: function () {
                    return {$promise: {then: function () {
                        return {results: []}
                    }}}
                }
            };
            endpointsMock = {
            };
            messageThreadsMock = {
                save: function(){}
            };
            usersServiceMock = {
                get: function (userId) {
                    return {$promise: {then: function () {
                        return {results: []}
                    }}}
                }
            };
            utilsServiceMock = {
                getIdFromUrl: function (url) {
                    return url;
                }
            };
            productRelatedMessagesParseServiceMock = {
                parseMessage: function (messageData, senderData) {
                }
            };

            module(function ($provide) {
                $provide.value("ProductRelatedMessages", productRelatedMessagesMock);
                $provide.value("Endpoints", endpointsMock);
                $provide.value("MessageThreads", messageThreadsMock);
                $provide.value("UsersService", usersServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
                $provide.value("ProductRelatedMessagesParseService", productRelatedMessagesParseServiceMock);
            });
        });

        beforeEach(inject(function (_ProductRelatedMessagesLoadService_, $q) {
            ProductRelatedMessagesLoadService = _ProductRelatedMessagesLoadService_;
            q = $q;
            spyOn(productRelatedMessagesMock, "get").and.callThrough();
            spyOn(productRelatedMessagesMock, "save").and.callThrough();
            spyOn(productRelatedMessagesMock, "update").and.callThrough();
            spyOn(messageThreadsMock, "save").and.callThrough();
            spyOn(usersServiceMock, "get").and.callThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").and.callThrough();
            spyOn(productRelatedMessagesParseServiceMock, "parseMessage").and.callThrough();
        }));

        it("ProductRelatedMessagesLoadService should be not null", function () {
            expect(!!ProductRelatedMessagesLoadService).toBe(true);
        });

        it("ProductRelatedMessagesLoadService:getMessage", function () {
            var messageId = 1;
            ProductRelatedMessagesLoadService.getMessage(messageId);
            expect(productRelatedMessagesMock.get).toHaveBeenCalledWith({id: messageId, _cache: jasmine.any(Number)})
        });

        it("ProductRelatedMessagesLoadService:postMessage", function () {
            var threadId = null, senderId = 2, recipientId = 3, text = "msg", offerId = 4, productId = 5;
            ProductRelatedMessagesLoadService.postMessage(threadId, senderId, recipientId, text, offerId, productId);
            expect(messageThreadsMock.save).toHaveBeenCalled();
        });

        it("ProductRelatedMessagesLoadService:updateMessage", function () {
            var message = {id: 1};
            ProductRelatedMessagesLoadService.updateMessage(message);
            expect(productRelatedMessagesMock.update).toHaveBeenCalledWith({id: message.id}, message);
        });
    });
});
