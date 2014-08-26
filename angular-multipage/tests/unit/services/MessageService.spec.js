define(["angular-mocks", "eloue/modules/booking/services/MessageService"], function () {

    describe("Service: MessageService", function () {

        var MessageService, usersResourceMock, messageThreadsResourceMock , productRelatedMessagesResourceMock;

        beforeEach(module("EloueApp"));

        beforeEach(function () {
            usersResourceMock = {get: function () {
            }};
            messageThreadsResourceMock = {list: function () {
                return {$promise: {then: function () {
                    return {results: [
                        {messages: [
                            "http://10.0.0.111:8000/api/2.0/productrelatedmessages/28394/"
                        ]}
                    ]}
                }}}
            }, save: function () {
            }};
            productRelatedMessagesResourceMock = {get: function () {
            }, save: function () {
            }};

            module(function ($provide) {
                $provide.value("Users", usersResourceMock);
                $provide.value("MessageThreads", messageThreadsResourceMock);
                $provide.value("ProductRelatedMessages", productRelatedMessagesResourceMock);
            });
        });

        beforeEach(inject(function (_MessageService_) {
            MessageService = _MessageService_;
            spyOn(usersResourceMock, "get").andCallThrough();
            spyOn(messageThreadsResourceMock, "list").andCallThrough();
            spyOn(messageThreadsResourceMock, "save").andCallThrough();
            spyOn(productRelatedMessagesResourceMock, "get").andCallThrough();
            spyOn(productRelatedMessagesResourceMock, "save").andCallThrough();
        }));

        it("MessageService should be not null", function () {
            expect(!!MessageService).toBe(true);
        });

        it("MessageService should have functions", function () {
            expect(angular.isFunction(MessageService.getMessageThread)).toBe(true);
            expect(angular.isFunction(MessageService.sendMessage)).toBe(true);
        });

        it("MessageService getMessageThread", function () {
            var productId = 1;
            MessageService.getMessageThread(productId);
            expect(messageThreadsResourceMock.list).toHaveBeenCalledWith({product: productId});
        });

        it("MessageService send message", function () {
            var productId = 1;
            var message = {
                sender: "http://10.0.0.111:8000/api/2.0/users/11/",
                recipient: "http://10.0.0.111:8000/api/2.0/users/22/",
                thread: "http://10.0.0.111:8000/api/2.0/messagethreads/111/",
                body: "test"
            };
            MessageService.sendMessage(message, productId);
        });
    });
});
