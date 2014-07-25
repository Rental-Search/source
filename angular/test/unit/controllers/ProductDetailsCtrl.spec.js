define(["angular-mocks", "eloue/modules/booking/controllers/ProductDetailsCtrl"], function () {

    describe("Controller: ProductDetailsCtrl", function () {

        var ProductDetailsCtrl,
            scope,
            route,
            productServiceMock,
            priceServiceMock,
            messageServiceMock,
            userServiceMock,
            endpointsMock;

        beforeEach(module("EloueApp"));
        beforeEach(module("EloueApp.BookingModule"));

        beforeEach(function () {
            productServiceMock = {getProduct: function () {
            }, isAvailable: function () {
            }};
            priceServiceMock = {getPricePerDay: function () {
            }};
            messageServiceMock = {getMessageThread: function () {
            }, sendMessage: function () {
            }};
            userServiceMock = {getUser: function () {
            }};
            endpointsMock = {
                api_url: "http://10.0.0.111:8000/api/2.0/"
            };

            module(function ($provide) {
                $provide.value("ProductService", productServiceMock);
                $provide.value("PriceService", priceServiceMock);
                $provide.value("MessageService", messageServiceMock);
                $provide.value("UserService", userServiceMock);
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
            route = {
                current: {
                    params: {
                        productId: 1
                    }
                }
            };
            spyOn(productServiceMock, "getProduct").andCallThrough();
            spyOn(productServiceMock, "isAvailable").andCallThrough();
            spyOn(priceServiceMock, "getPricePerDay").andCallThrough();
            spyOn(messageServiceMock, "getMessageThread").andCallThrough();
            spyOn(messageServiceMock, "sendMessage").andCallThrough();
            spyOn(userServiceMock, "getUser").andCallThrough();

            ProductDetailsCtrl = $controller("ProductDetailsCtrl", { $scope: scope, $route: route, ProductService: productServiceMock,
                PriceService: priceServiceMock, MessageService: messageServiceMock, UserService: userServiceMock, Endpoints: endpointsMock});
        }));

        it("ProductDetailsCtrl should be not null", function () {
            expect(!!ProductDetailsCtrl).toBe(true);
        });

        it("ProductDetailsCtrl updatePrice", function () {
            scope.updatePrice();
        });

        it("ProductDetailsCtrl sendMessage", function () {
            scope.sendMessage();
        });
    });
});