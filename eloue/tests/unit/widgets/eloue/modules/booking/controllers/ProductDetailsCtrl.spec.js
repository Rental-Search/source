define(["angular-mocks", "datejs", "eloue/modules/booking/controllers/ProductDetailsCtrl"], function () {

    describe("Controller: ProductDetailsCtrl", function () {

        var ProductDetailsCtrl,
            scope,
            window,
            location,
            productsLoadServiceMock,
            messageThreadsServiceMock,
            usersServiceMock,
            authServiceMock,
            endpointsMock,
            civilityChoicesMock,
            productRelatedMessagesLoadServiceMock,
            addressesServiceMock,
            creditCardsServiceMock,
            bookingsLoadServiceMock,
            bookingsServiceMock,
            phoneNumbersServiceMock,
            categoriesServiceMock,
            utilsServiceMock;

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
                getMe: function () {
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
                $provide.value("CivilityChoices", civilityChoicesMock);
                $provide.value("ProductRelatedMessagesLoadService", productRelatedMessagesLoadServiceMock);
                $provide.value("AddressesService", addressesServiceMock);
                $provide.value("CreditCardsService", creditCardsServiceMock);
                $provide.value("BookingsLoadService", bookingsLoadServiceMock);
                $provide.value("BookingsService", bookingsServiceMock);
                $provide.value("PhoneNumbersService", phoneNumbersServiceMock);
                $provide.value("CategoriesService", categoriesServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
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
            scope.currentUserPromise = {then: function () {
                return {response: {}}
            }};
            scope.currentUser = {
                id: 111
            };
            scope.product = {owner: { id: 111}};
            window = {location: {href: "location/sdsdfdfsdfsd/sdfsdfsd/sddfsdf/fdff-123"}};
            location = {};
            civilityChoicesMock = {};
            productRelatedMessagesLoadServiceMock = {};
            addressesServiceMock = {};
            creditCardsServiceMock = {};
            bookingsLoadServiceMock = {};
            bookingsServiceMock = {};
            phoneNumbersServiceMock = {};
            categoriesServiceMock = {};
            utilsServiceMock = {};
            spyOn(productsLoadServiceMock, "getProduct").andCallThrough();
            spyOn(productsLoadServiceMock, "isAvailable").andCallThrough();
            spyOn(messageThreadsServiceMock, "getMessageThread").andCallThrough();
            spyOn(messageThreadsServiceMock, "sendMessage").andCallThrough();
            spyOn(usersServiceMock, "get").andCallThrough();
            spyOn(usersServiceMock, "getMe").andCallThrough();
            spyOn(authServiceMock, "getCookie").andCallThrough();
            ProductDetailsCtrl = $controller("ProductDetailsCtrl", {
                $scope: scope, $window: window, $location: location, Endpoints: endpointsMock,
                CivilityChoices: civilityChoicesMock,
                ProductsLoadService: productsLoadServiceMock,
                MessageThreadsService: messageThreadsServiceMock,
                ProductRelatedMessagesLoadService: productRelatedMessagesLoadServiceMock,
                UsersService: usersServiceMock,
                AuthService: authServiceMock,
                AddressesService: addressesServiceMock,
                CreditCardsService: creditCardsServiceMock,
                BookingsLoadService: bookingsLoadServiceMock,
                BookingsService: bookingsServiceMock,
                PhoneNumbersService: phoneNumbersServiceMock,
                CategoriesService: categoriesServiceMock,
                UtilsService: utilsServiceMock
            });
        }));

        it("ProductDetailsCtrl should be not null", function () {
            expect(!!ProductDetailsCtrl).toBe(true);
        });

        it("ProductDetailsCtrl:updatePrice", function () {
            scope.updatePrice();
        });

        it("ProductDetailsCtrl:loadMessageThread", function () {
            scope.loadMessageThread();
        });
    });
});