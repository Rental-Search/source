define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: ProductsService", function () {

        var ProductsService,
            addressesServiceMock,
            bookingsResourceMock,
            productsResourceMock,
            categoriesServiceMock,
            phoneNumbersServiceMock,
            picturesServiceMock,
            pricesServiceMock,
            utilsServiceMock,
            usersServiceMock,
            messageThreadsResourceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            addressesServiceMock = {

            };
            bookingsResourceMock = {

            };
            productsResourceMock = {

            };
            categoriesServiceMock = {

            };
            phoneNumbersServiceMock = {

            };
            picturesServiceMock = {

            };
            pricesServiceMock = {

            };
            utilsServiceMock = {

            };
            usersServiceMock = {

            };
            messageThreadsResourceMock = {

            };

            module(function ($provide) {
                $provide.value("AddressesService", addressesServiceMock);
                $provide.value("Bookings", bookingsResourceMock);
                $provide.value("Products", productsResourceMock);
                $provide.value("CategoriesService", categoriesServiceMock);
                $provide.value("PhoneNumbersService", phoneNumbersServiceMock);
                $provide.value("PicturesService", picturesServiceMock);
                $provide.value("PricesService", pricesServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
                $provide.value("UsersService", usersServiceMock);
                $provide.value("MessageThreads", messageThreadsResourceMock);
            });
        });

        beforeEach(inject(function (_ProductsService_) {
            ProductsService = _ProductsService_;
        }));

        it("ProductsService should be not null", function () {
            expect(!!ProductsService).toBe(true);
        });
    });
});