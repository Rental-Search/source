define(["angular-mocks", "datejs", "eloue/modules/booking/controllers/ProductDetailsCtrl"], function () {

    describe("Controller: ProductDetailsCtrl", function () {

        var ProductDetailsCtrl,
            scope,
            route,
            location,
            productsLoadServiceMock,
            messageThreadsServiceMock,
            usersServiceMock,
            authServiceMock,
            endpointsMock;

        beforeEach(module("EloueApp.BookingModule"));

        beforeEach(function () {
            productsLoadServiceMock = {getProduct: function () {
                return {
                    then: function () {
                        return {result: {}}
                    }
                }
            }, isAvailable: function () {
                return {then: function () {
                    return {result: {}}
                }}
            }};
            messageThreadsServiceMock = {getMessageThread: function () {
                return {
                    then: function () {
                        return {result: {}}
                    }
                }
            }, sendMessage: function () {
                return {
                    then: function () {
                        return {result: {}}
                    }
                }
            }};
            usersServiceMock = {
                get: function (userId) {
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                },
                getMe: function() {
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                }
            };
            authServiceMock = {
                getCookie: function (cookieName) {

                }
            };
                endpointsMock = {
                    api_url: "http://10.0.0.111:8000/api/2.0/"
                };

            module(function ($provide) {
                $provide.value("ProductsLoadService", productsLoadServiceMock);
                $provide.value("MessageThreadsService", messageThreadsServiceMock);
                $provide.value("UserService", usersServiceMock);
                $provide.value("AuthService", authServiceMock);
                $provide.value("Endpoints", endpointsMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            scope.bookingDetails = {
                "fromDate": "",
                "fromHour": "08:00:00",
                "toDate": "",
                "toHour": "08:00:00"
            };
            scope.currentUser = {
                id: 111
            };
            scope.product = {owner: { id: 111}};
            route = {
                current: {
                    params: {
                        productId: 1
                    }
                }
            };
            location = {};
            spyOn(productsLoadServiceMock, "getProduct").andCallThrough();
            spyOn(productsLoadServiceMock, "isAvailable").andCallThrough();
            spyOn(messageThreadsServiceMock, "getMessageThread").andCallThrough();
            spyOn(messageThreadsServiceMock, "sendMessage").andCallThrough();
            spyOn(usersServiceMock, "get").andCallThrough();
            spyOn(usersServiceMock, "getMe").andCallThrough();
            spyOn(authServiceMock, "getCookie").andCallThrough();
            ProductDetailsCtrl = $controller("ProductDetailsCtrl", {
                $scope: scope, $route: route, $location: location, ProductsLoadService: productsLoadServiceMock,
                MessageThreadsService: messageThreadsServiceMock, UsersService: usersServiceMock, Endpoints: endpointsMock
            });
        }));

        it("ProductDetailsCtrl should be not null", function () {
            expect(!!ProductDetailsCtrl).toBe(true);
        });

        it("ProductDetailsCtrl:updatePrice", function () {
            scope.updatePrice();
        });

        it("ProductDetailsCtrl:sendMessage", function () {
            scope.sendMessage();
        });

        it("ProductDetailsCtrl:loadMessageThread", function () {
            scope.loadMessageThread();
            expect(messageThreadsServiceMock.getMessageThread).toHaveBeenCalled();
        });

        it("ProductDetailsCtrl:loadProductDetails", function () {
            scope.loadProductDetails();
            expect(productsLoadServiceMock.getProduct).toHaveBeenCalled();
        });
    });
});