define(["angular-mocks", "eloue/controllers/messages/MessageDetailCtrl"], function () {

    describe("Controller: MessageDetailCtrl", function () {

        var MessageDetailCtrl,
            scope,
            q,
            window,
            utilsServiceMock,
            stateParams,
            endpointsMock,
            messageThreadsLoadServiceMock,
            bookingsLoadServiceMock,
            productRelatedMessagesLoadServiceMock,
            productsLoadServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            utilsServiceMock = {
                getIdFromUrl: function (url) {

                },
                calculatePeriodBetweenDates: function (startDateString, endDateString) {

                },
                formatDate: function (date, format) {

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
                    return {
                        $promise: {
                            then: function () {
                                return {result: {}}
                            }
                        }
                    }
                },
                postMessage: function (threadId, senderId, recipientId, text, offerId, productId) {
                    return {
                        then: function (productId) {
                            return {result: {}}
                        }
                    }
                }
            };

            productsLoadServiceMock = {
                getAbsoluteUrl: function (id) {
                    return {
                        $promise: {
                            then: function () {
                                return {result: {}}
                            }
                        }
                    }
                },
                isAvailable: function (id, startDate, endDate, quantity) {
                    return {
                        then: function (productId) {
                            return {result: {}}
                        }
                    }
                }
            };

            q = {
                all: function (obj) {
                    return {then: function () {
                    }}
                }
            };

            module(function ($provide) {
                $provide.value("UtilsService", utilsServiceMock);
                $provide.value("MessageThreadsLoadService", messageThreadsLoadServiceMock);
                $provide.value("BookingsLoadService", bookingsLoadServiceMock);
                $provide.value("ProductRelatedMessagesLoadService", productRelatedMessagesLoadServiceMock);
                $provide.value("ProductsLoadService", productsLoadServiceMock);
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

            spyOn(utilsServiceMock, "getIdFromUrl").and.callThrough();
            spyOn(utilsServiceMock, "calculatePeriodBetweenDates").and.callThrough();
            spyOn(utilsServiceMock, "formatDate").and.callThrough();
            spyOn(messageThreadsLoadServiceMock, "getMessageThread").and.callThrough();
            spyOn(messageThreadsLoadServiceMock, "getUsersRoles").and.callThrough();
            spyOn(bookingsLoadServiceMock, "getBookingByProduct").and.callThrough();
            spyOn(productRelatedMessagesLoadServiceMock, "updateMessage").and.callThrough();
            spyOn(productRelatedMessagesLoadServiceMock, "postMessage").and.callThrough();
            spyOn(productsLoadServiceMock, "getAbsoluteUrl").and.callThrough();
            spyOn(productsLoadServiceMock, "isAvailable").and.callThrough();
            spyOn(q, "all").and.callThrough();

            MessageDetailCtrl = $controller('MessageDetailCtrl', { $scope: scope, $stateParams: stateParams, $q: q, $window: window,
                Endpoints: endpointsMock, MessageThreadsLoadService: messageThreadsLoadServiceMock,
                BookingsLoadService: bookingsLoadServiceMock, ProductRelatedMessagesLoadService: productRelatedMessagesLoadServiceMock,
                ProductsLoadService: productsLoadServiceMock, UtilsService: utilsServiceMock });
        }));

        it("MessageDetailCtrl should be not null", function () {
            expect(!!MessageDetailCtrl).toBe(true);
        });
    });
});