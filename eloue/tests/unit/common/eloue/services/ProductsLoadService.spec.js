define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: ProductsLoadService", function () {

        var ProductsLoadService,
            productsMock,
            checkAvailabilityMock,
            addressesServiceMock,
            usersServiceMock,
            phoneNumbersServiceMock,
            utilsServiceMock,
            productsParseServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            productsMock = {
                get: function () {
                }
            };
            checkAvailabilityMock = {
                get: function () {
                }
            };
            addressesServiceMock = {
                getAddress: function (addressId) {

                }
            };
            usersServiceMock = {
                get: function (userId) {
                }
            };
            phoneNumbersServiceMock = {
                getPhoneNumber: function (phoneId) {

                }
            };
            utilsServiceMock = {
                getIdFromUrl: function (url) {
                }
            };
            productsParseServiceMock = {
                parseProduct: function (productData, statsData, address, owner, ownerStats, phone, pictures) {
                }
            };

            module(function ($provide) {
                $provide.value("Products", productsMock);
                $provide.value("CheckAvailability", checkAvailabilityMock);
                $provide.value("AddressesService", addressesServiceMock);
                $provide.value("UsersService", usersServiceMock);
                $provide.value("PhoneNumbersService", phoneNumbersServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
                $provide.value("ProductsParseService", productsParseServiceMock);
            });
        });

        beforeEach(inject(function (_ProductsLoadService_) {
            ProductsLoadService = _ProductsLoadService_;
            spyOn(productsMock, "get").and.callThrough();
            spyOn(checkAvailabilityMock, "get").and.callThrough();
            spyOn(addressesServiceMock, "getAddress").and.callThrough();
            spyOn(usersServiceMock, "get").and.callThrough();
            spyOn(phoneNumbersServiceMock, "getPhoneNumber").and.callThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").and.callThrough();
            spyOn(productsParseServiceMock, "parseProduct").and.callThrough();
        }));

        it("ProductsLoadService should be not null", function () {
            expect(!!ProductsLoadService).toBe(true);
        });
    });
});