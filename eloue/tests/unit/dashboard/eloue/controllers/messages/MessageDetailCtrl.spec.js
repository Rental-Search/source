define(["angular-mocks", "eloue/controllers/messages/MessageDetailCtrl"], function () {

    describe("Controller: MessageDetailCtrl", function () {

        var MessageDetailCtrl,
            scope,
            q,
            window,
            utilsServiceMock,
            stateParams,
            endpointsMock,
            messageThreadsServiceMock,
            bookingsServiceMock,
            productRelatedMessagesServiceMock,
            productsServiceMock;

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

            messageThreadsServiceMock = {
                getMessageThreadById: function (threadId) {
                    console.log("messageThreadsServiceMock:getMessageThreadById called with threadId = " + threadId);
                    return {then: function () {
                    }}
                },
                getUsersRoles: function (messageThread, currentUserId) {
                    return {recipientId: 1, senderId: 1};
                }
            };

            bookingsServiceMock = {
                getBookingByProduct: function (productId) {
                    console.log("bookingsServiceMock:getBookingByProduct called with productId = " + productId);
                    return {then: function () {
                    }}
                }
            };

            productRelatedMessagesServiceMock = {
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

            productsServiceMock = {
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
                $provide.value("MessageThreadsService", messageThreadsServiceMock);
                $provide.value("BookingsService", bookingsServiceMock);
                $provide.value("ProductRelatedMessagesService", productRelatedMessagesServiceMock);
                $provide.value("ProductsService", productsServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            scope.showNotification = function(object, action, bool){};
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
            spyOn(messageThreadsServiceMock, "getMessageThreadById").and.callThrough();
            spyOn(messageThreadsServiceMock, "getUsersRoles").and.callThrough();
            spyOn(bookingsServiceMock, "getBookingByProduct").and.callThrough();
            spyOn(productRelatedMessagesServiceMock, "updateMessage").and.callThrough();
            spyOn(productRelatedMessagesServiceMock, "postMessage").and.callThrough();
            spyOn(productsServiceMock, "getAbsoluteUrl").and.callThrough();
            spyOn(productsServiceMock, "isAvailable").and.callThrough();
            spyOn(q, "all").and.callThrough();

            MessageDetailCtrl = $controller('MessageDetailCtrl', { $scope: scope, $stateParams: stateParams, $q: q, $window: window,
                Endpoints: endpointsMock, MessageThreadsService: messageThreadsServiceMock,
                BookingsService: bookingsServiceMock, ProductRelatedMessagesService: productRelatedMessagesServiceMock,
                ProductsService: productsServiceMock, UtilsService: utilsServiceMock });
        }));

        it("MessageDetailCtrl should be not null", function () {
            expect(!!MessageDetailCtrl).toBe(true);
        });
    });
});