define(["angular-mocks", "eloue/controllers/messages/NewMessageThreadCtrl"], function () {

    describe("Controller: NewMessageThreadCtrl", function () {

        var NewMessageThreadCtrl,
            scope,
            state,
            stateParams,
            endpointsMock,
            bookingsServiceMock,
            productRelatedMessagesServiceMock,
            productsServiceMock,
            utilsServiceMock,
            usersServiceMock,
            simpleServiceResponse = {
                then: function () {
                    return {result: {}};
                }
            };

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            endpointsMock = {
                api_url: "/api/2.0/"
            };
            bookingsServiceMock = {
                getBookingByProduct: function (productId) {
                    return simpleServiceResponse;
                }
            };
            productRelatedMessagesServiceMock = {
                postMessage: function (threadId, senderId, recipientId, text, offerId, productId) {
                    return simpleServiceResponse;
                }
            };
            productsServiceMock = {
                getProduct: function (productId, loadProductStats, loadOwnerStats) {
                    return simpleServiceResponse;
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
                $provide.value("BookingsService", bookingsServiceMock);
                $provide.value("ProductRelatedMessagesService", productRelatedMessagesServiceMock);
                $provide.value("ProductsService", productsServiceMock);
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
            spyOn(bookingsServiceMock, "getBookingByProduct").and.callThrough();
            spyOn(productRelatedMessagesServiceMock, "postMessage").and.callThrough();
            spyOn(productsServiceMock, "getProduct").and.callThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").and.callThrough();

            NewMessageThreadCtrl = $controller('NewMessageThreadCtrl', {
                $scope: scope, $state: state,
                $stateParams: stateParams, Endpoints: endpointsMock, BookingsService: bookingsServiceMock,
                ProductRelatedMessagesService: productRelatedMessagesServiceMock,
                ProductsService: productsServiceMock, UtilsService: utilsServiceMock,
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