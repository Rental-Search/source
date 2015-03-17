define(["angular-mocks", "eloue/services/ProductRelatedMessagesService"], function () {

    describe("Service: ProductRelatedMessagesService", function () {

        var ProductRelatedMessagesService,
            q,
            productRelatedMessagesMock,
            endpointsMock,
            messageThreadsMock,
            usersServiceMock,
            utilsServiceMock,
            simpleResourceResponse = {
                $promise: {
                    then: function () {
                        return {results: []};
                    }
                }
            };

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            productRelatedMessagesMock = {
                get: function () {
                    return simpleResourceResponse;
                },
                save: function () {
                    return simpleResourceResponse;
                },
                update: function () {
                    return simpleResourceResponse;
                }
            };
            endpointsMock = {
            };
            messageThreadsMock = {
                save: function(){
                    return simpleResourceResponse;
                }
            };
            usersServiceMock = {
                get: function (userId) {
                    return simpleResourceResponse;
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

        it("ProductRelatedMessagesService:getThreadMessages", function() {
            var threadId = 1, page = 1;
            ProductRelatedMessagesService.getThreadMessages(threadId, page);
            expect(productRelatedMessagesMock.get).toHaveBeenCalled();
            expect(productRelatedMessagesMock.get).toHaveBeenCalledWith({thread: threadId, _cache: jasmine.any(Number), ordering: '-sent_at', page: page});
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
