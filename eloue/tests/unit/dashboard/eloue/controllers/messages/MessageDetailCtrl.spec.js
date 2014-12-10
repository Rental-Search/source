define(["angular-mocks", "eloue/controllers/messages/MessageDetailCtrl"], function () {

    describe("Controller: MessageDetailCtrl", function () {

        var MessageDetailCtrl,
            scope,
            q,
            window,
            usersServiceMock,
            stateParams,
            endpointsMock,
            messageThreadsLoadServiceMock,
            bookingsLoadServiceMock,
            productRelatedMessagesLoadServiceMock,
            productsLoadServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            usersServiceMock = {
                getMe: function (successCallback, errorCallback) {
                    console.log("usersServiceMock:getMe");
                    return { id: 1190};
                }
            };

            endpointsMock = {
                api_url: "/api/2.0/"
            };

            messageThreadsLoadServiceMock = {
                getMessageThread: function (threadId) {
                    console.log("messageThreadsLoadServiceMock:getMessageThread called with threadId = " + threadId);
                    return {then: function () {
                    }}
                },
                getUsersRoles: function (messageThread, currentUserId) {
                    return {recipientId: 1, senderId: 1};
                }
            };

            bookingsLoadServiceMock = {
                getBookingByProduct: function (productId) {
                    console.log("bookingsLoadServiceMock:getBookingByProduct called with productId = " + productId);
                    return {then: function () {
                    }}
                }
            };

            productRelatedMessagesLoadServiceMock = {
                updateMessage: function (message) {

                },
            postMessage: function (threadId, senderId, recipientId, text, offerId, productId) {

            }
            };

            productsLoadServiceMock = {

            };

            q = {
                all: function (obj) {
                    return {then: function () {
                    }}
                }
            };

            module(function ($provide) {
                $provide.value("UsersService", usersServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            window = {
                location: {
                    href: ""
                }
            };
            stateParams = {
                id: 1
            };

            spyOn(usersServiceMock, "getMe").and.callThrough();

            MessageDetailCtrl = $controller('MessageDetailCtrl', { $scope: scope, $stateParams: stateParams, $q: q, $window: window,
                Endpoints: endpointsMock, MessageThreadsLoadService: messageThreadsLoadServiceMock,
                BookingsLoadService: bookingsLoadServiceMock, ProductRelatedMessagesLoadService: productRelatedMessagesLoadServiceMock,
                ProductsLoadService: productsLoadServiceMock, UsersService: usersServiceMock });
        }));

        it("MessageDetailCtrl should be not null", function () {
            expect(!!MessageDetailCtrl).toBe(true);
        });
    });
});