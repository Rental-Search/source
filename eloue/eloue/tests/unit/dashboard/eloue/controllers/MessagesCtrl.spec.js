define(["angular-mocks", "eloue/controllers/MessagesCtrl"], function() {

    describe("Controller: MessagesCtrl", function () {

        var MessagesCtrl,
            scope,
            messageThreadsLoadServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            messageThreadsLoadServiceMock = {
                getMessageThreadList: function (loadSender, loadLastMessage) {
                    console.log("messageThreadsLoadServiceMock:getMessageThreadList called with loadSender = " + loadSender + ", loadLastMessage = " + loadLastMessage);
                    return {then: function () {
                        return {response: {}}
                    }}
                }
            };

            module(function($provide) {
                $provide.value("MessageThreadsLoadService", messageThreadsLoadServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();

            spyOn(messageThreadsLoadServiceMock, "getMessageThreadList").andCallThrough();

            MessagesCtrl = $controller('MessagesCtrl', { $scope: scope, MessageThreadsLoadService: messageThreadsLoadServiceMock });
            expect(messageThreadsLoadServiceMock.getMessageThreadList).toHaveBeenCalledWith(true, true);
        }));

        it("MessagesCtrl should be not null", function () {
            expect(!!MessagesCtrl).toBe(true);
        });
    });
});