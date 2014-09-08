define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: ProductsLoadService", function () {

        var ProductsLoadService,
            productsMock,
            checkAvailabilityMock,
            addressesServiceMock,
            usersServiceMock,
            picturesServiceMock,
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
            picturesServiceMock = {
                getPicturesByProduct: function (productId) {

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
                parseProduct: function (productData, address, owner, phone, pictures) {
                }
            };

            module(function ($provide) {
                $provide.value("Products", productsMock);
                $provide.value("CheckAvailability", checkAvailabilityMock);
                $provide.value("AddressesService", addressesServiceMock);
                $provide.value("UsersService", usersServiceMock);
                $provide.value("PicturesService", picturesServiceMock);
                $provide.value("PhoneNumbersService", phoneNumbersServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
                $provide.value("ProductsParseService", productsParseServiceMock);
            });
        });

        beforeEach(inject(function (_ProductsLoadService_) {
            ProductsLoadService = _ProductsLoadService_;
            spyOn(productsMock, "get").andCallThrough();
            spyOn(checkAvailabilityMock, "get").andCallThrough();
            spyOn(addressesServiceMock, "getAddress").andCallThrough();
            spyOn(usersServiceMock, "get").andCallThrough();
            spyOn(picturesServiceMock, "getPicturesByProduct").andCallThrough();
            spyOn(phoneNumbersServiceMock, "getPhoneNumber").andCallThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").andCallThrough();
            spyOn(productsParseServiceMock, "parseProduct").andCallThrough();
        }));

        it("ProductsLoadService should be not null", function () {
            expect(!!ProductsLoadService).toBe(true);
        });
    });
});