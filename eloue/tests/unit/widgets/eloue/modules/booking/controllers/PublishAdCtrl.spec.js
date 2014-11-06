define(["angular-mocks", "datejs", "eloue/modules/booking/controllers/PublishAdCtrl"], function () {

    describe("Controller: PublishAdCtrl", function () {

        var PublishAdCtrl,
            scope,
            window,
            location,
            endpointsMock,
            utilsServiceMock,
            unitMock,
            currencyMock,
            productsServiceMock,
            usersServiceMock,
            addressesServiceMock,
            authServiceMock,
            categoriesServiceMock,
            pricesServiceMock;

        beforeEach(module("EloueApp.BookingModule"));

        beforeEach(function () {
            endpointsMock = {
                api_url: "http://10.0.0.111:8000/api/2.0/"
            };
            unitMock = {DAY: {id: 1}};
            currencyMock = {};
            productsServiceMock = {};
            usersServiceMock = {};
            addressesServiceMock = {};
            authServiceMock = {
                getCookie: function (cookieName) {

                }
            };
            categoriesServiceMock = {};
            pricesServiceMock = {};

            module(function ($provide) {
                $provide.value("Endpoints", endpointsMock);
                $provide.value("Unit", unitMock);
                $provide.value("Currency", currencyMock);
                $provide.value("ProductsService", productsServiceMock);
                $provide.value("UsersService", usersServiceMock);
                $provide.value("AddressesService", addressesServiceMock);
                $provide.value("AuthService", authServiceMock);
                $provide.value("CategoriesService", categoriesServiceMock);
                $provide.value("PricesService", pricesServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            scope.currentUserPromise = {then: function () {
                return {response: {}}
            }};
            scope.currentUser = {
                id: 111
            };
            window = {location: {href: "location/sdsdfdfsdfsd/sdfsdfsd/sddfsdf/fdff-123"}};
            location = {};
            utilsServiceMock = {};
            PublishAdCtrl = $controller("PublishAdCtrl", {
                $scope: scope, $window: window, $location: location, Endpoints: endpointsMock,
                Unit: unitMock,
                Currency: currencyMock,
                ProductsService: productsServiceMock,
                UsersService: usersServiceMock,
                AddressesService: addressesServiceMock,
                AuthService: authServiceMock,
                CategoriesService: categoriesServiceMock,
                PricesService: pricesServiceMock,
                UtilsService: utilsServiceMock
            });
        }));

        it("PublishAdCtrl should be not null", function () {
            expect(!!PublishAdCtrl).toBe(true);
        });
    });
});
