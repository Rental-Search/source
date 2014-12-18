define(["angular-mocks", "eloue/controllers/messages/NewMessageThreadCtrl"], function () {

    describe("Controller: NewMessageThreadCtrl", function () {

        var NewMessageThreadCtrl,
            scope,
            state,
            stateParams,
            endpointsMock,
            bookingsLoadServiceMock,
            productRelatedMessagesLoadServiceMock,
            productsLoadServiceMock,
            utilsServiceMock,
            usersServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            endpointsMock = {
                api_url: "/api/2.0/"
            };
            bookingsLoadServiceMock = {
                getBookingByProduct: function (productId) {
                    return {
                        then: function (productId) {
                            return {result: {}}
                        }
                    }
                }
            };
            productRelatedMessagesLoadServiceMock = {
                postMessage: function (threadId, senderId, recipientId, text, offerId, productId) {
                    return {
                        then: function (productId) {
                            return {result: {}}
                        }
                    }
                }
            };
            productsLoadServiceMock = {
                getProduct: function (productId, loadProductStats, loadOwnerStats) {
                    return {
                        then: function (productId) {
                            return {result: {}}
                        }
                    }
                }
            };
            utilsServiceMock = {
                getIdFromUrl: function (url) {

                }
            };
            usersServiceMock = {
                getMe: function (successCallback, errorCallback) {
                    console.log("usersServiceMock:getMe");
                    return {id: 1190};
                }
            };

            module(function ($provide) {
                $provide.value("Endpoints", endpointsMock);
                $provide.value("BookingsLoadService", bookingsLoadServiceMock);
                $provide.value("ProductRelatedMessagesLoadService", productRelatedMessagesLoadServiceMock);
                $provide.value("ProductsLoadService", productsLoadServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
                $provide.value("UsersService", usersServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            scope.currentUserPromise = {
                then: function () {
                }
            };
            scope.showNotification = function(object, action, bool){};
            state = {};
            stateParams = {
                id: 1
            };

            spyOn(usersServiceMock, "getMe").and.callThrough();
            spyOn(bookingsLoadServiceMock, "getBookingByProduct").and.callThrough();
            spyOn(productRelatedMessagesLoadServiceMock, "postMessage").and.callThrough();
            spyOn(productsLoadServiceMock, "getProduct").and.callThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").and.callThrough();

            NewMessageThreadCtrl = $controller('NewMessageThreadCtrl', {
                $scope: scope, $state: state,
                $stateParams: stateParams, Endpoints: endpointsMock, BookingsLoadService: bookingsLoadServiceMock,
                ProductRelatedMessagesLoadService: productRelatedMessagesLoadServiceMock,
                ProductsLoadService: productsLoadServiceMock, UtilsService: utilsServiceMock,
                UsersService: usersServiceMock
            });
        }));

        it("NewMessageThreadCtrl should be not null", function () {
            expect(!!NewMessageThreadCtrl).toBe(true);
        });

        it("NewMessageThreadCtrl:postNewMessage", function () {
            scope.currentUser = {id: 1};
            scope.messageThread = {id: 1};
            scope.booking = {owner: {}};
            scope.postNewMessage();
        });
    });
});