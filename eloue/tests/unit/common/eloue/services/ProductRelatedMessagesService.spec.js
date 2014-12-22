define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: ProductRelatedMessagesService", function () {

        var ProductRelatedMessagesService,
            q,
            productRelatedMessagesMock,
            endpointsMock,
            messageThreadsMock,
            usersServiceMock,
            utilsServiceMock;

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

            module(function ($provide) {
                $provide.value("ProductRelatedMessages", productRelatedMessagesMock);
                $provide.value("Endpoints", endpointsMock);
                $provide.value("MessageThreads", messageThreadsMock);
                $provide.value("UsersService", usersServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
            });
        });

        beforeEach(inject(function (_ProductRelatedMessagesService_, $q) {
            ProductRelatedMessagesService = _ProductRelatedMessagesService_;
            q = $q;
            spyOn(productRelatedMessagesMock, "get").and.callThrough();
            spyOn(productRelatedMessagesMock, "save").and.callThrough();
            spyOn(productRelatedMessagesMock, "update").and.callThrough();
            spyOn(messageThreadsMock, "save").and.callThrough();
            spyOn(usersServiceMock, "get").and.callThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").and.callThrough();
        }));

        it("ProductRelatedMessagesService should be not null", function () {
            expect(!!ProductRelatedMessagesService).toBe(true);
        });

        it("ProductRelatedMessagesService:getMessage", function () {
            var messageId = 1;
            ProductRelatedMessagesService.getMessage(messageId);
            expect(productRelatedMessagesMock.get).toHaveBeenCalledWith({id: messageId, _cache: jasmine.any(Number)});
        });

        it("ProductRelatedMessagesService:getMessage", function () {
            var messageId = 1;
            ProductRelatedMessagesService.getMessage(messageId);
            expect(productRelatedMessagesMock.get).toHaveBeenCalledWith({id: messageId, _cache: jasmine.any(Number)})
        });

        it("ProductRelatedMessagesService:postMessage", function () {
            var threadId = null, senderId = 2, recipientId = 3, text = "msg", offerId = 4, productId = 5;
            ProductRelatedMessagesService.postMessage(threadId, senderId, recipientId, text, offerId, productId);
            expect(messageThreadsMock.save).toHaveBeenCalled();
        });

        it("ProductRelatedMessagesService:updateMessage", function () {
            var message = {id: 1};
            ProductRelatedMessagesService.updateMessage(message);
            expect(productRelatedMessagesMock.update).toHaveBeenCalledWith({id: message.id}, message);
        });

        it("ProductRelatedMessagesService:parseMessage", function () {
            var sender = "Author";
            var result = ProductRelatedMessagesService.parseMessage({}, sender);
            expect(result).toEqual({sender: sender});
        });
    });
});
