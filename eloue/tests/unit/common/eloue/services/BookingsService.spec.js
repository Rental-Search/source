define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: BookingsService", function () {

        var BookingsService,
            bookingsMock,
            productsMock,
            productsServiceMock,
            addressesServiceMock,
            usersServiceMock,
            phoneNumbersServiceMock,
            commentsServiceMock,
            utilsServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {

            bookingsMock = {
                get: function () {
                    return {$promise: {then: function () {
                        return {results: []}
                    }}}
                }
            };
            productsMock = {
                get: function () {
                    return {$promise: {then: function () {
                        return {results: []}
                    }}}
                }
            };
            productsServiceMock = {
                getProduct: function (productId) {

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
            commentsServiceMock = {
                getCommentList: function (bookingUUID) {

                }
            };
            utilsServiceMock = {
                formatDate: function (date, format) {

                }
            };

            module(function ($provide) {
                $provide.value("Bookings", bookingsMock);
                $provide.value("Products", productsMock);
                $provide.value("ProductsService", productsServiceMock);
                $provide.value("AddressesService", addressesServiceMock);
                $provide.value("UsersService", usersServiceMock);
                $provide.value("PhoneNumbersService", phoneNumbersServiceMock);
                $provide.value("CommentsService", commentsServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
            });
        });

        beforeEach(inject(function (_BookingsService_) {
            BookingsService = _BookingsService_;
            spyOn(bookingsMock, "get").and.callThrough();
            spyOn(productsMock, "get").and.callThrough();
            spyOn(productsServiceMock, "getProduct").and.callThrough();
            spyOn(addressesServiceMock, "getAddress").and.callThrough();
            spyOn(usersServiceMock, "get").and.callThrough();
            spyOn(phoneNumbersServiceMock, "getPhoneNumber").and.callThrough();
            spyOn(commentsServiceMock, "getCommentList").and.callThrough();
            spyOn(utilsServiceMock, "formatDate").and.callThrough();
        }));

        it("BookingsService should be not null", function () {
            expect(!!BookingsService).toBe(true);
        });

        it("BookingsService:getBookingsByProduct", function () {
            var productId = 1;
            BookingsService.getBookingsByProduct(productId);
            expect(bookingsMock.get).toHaveBeenCalledWith({product: productId, _cache: jasmine.any(Number)});
        });
    });
});