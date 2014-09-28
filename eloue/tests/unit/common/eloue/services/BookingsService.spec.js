define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: BookingsService", function () {

        var BookingsService,
            bookingsMock,
            productsMock,
            productsServiceMock,
            picturesServiceMock,
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
            picturesServiceMock = {
                getPicturesByProduct: function (productId) {

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
                $provide.value("PicturesService", picturesServiceMock);
                $provide.value("AddressesService", addressesServiceMock);
                $provide.value("UsersService", usersServiceMock);
                $provide.value("PhoneNumbersService", phoneNumbersServiceMock);
                $provide.value("CommentsService", commentsServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
            });
        });

        beforeEach(inject(function (_BookingsService_) {
            BookingsService = _BookingsService_;
            spyOn(bookingsMock, "get").andCallThrough();
            spyOn(productsMock, "get").andCallThrough();
            spyOn(productsServiceMock, "getProduct").andCallThrough();
            spyOn(picturesServiceMock, "getPicturesByProduct").andCallThrough();
            spyOn(addressesServiceMock, "getAddress").andCallThrough();
            spyOn(usersServiceMock, "get").andCallThrough();
            spyOn(phoneNumbersServiceMock, "getPhoneNumber").andCallThrough();
            spyOn(commentsServiceMock, "getCommentList").andCallThrough();
            spyOn(utilsServiceMock, "formatDate").andCallThrough();
        }));

        it("BookingsService should be not null", function () {
            expect(!!BookingsService).toBe(true);
        });

        it("BookingsService:getBookings", function () {
            var page = null;
            BookingsService.getBookings(page);
            expect(bookingsMock.get).toHaveBeenCalledWith({page: page});
        });

        it("BookingsService:getBookingsByProduct", function () {
            var productId = 1;
            BookingsService.getBookingsByProduct(productId);
            expect(bookingsMock.get).toHaveBeenCalledWith({product: productId});
        });

        it("BookingsService:getBooking", function () {
            var uuid = 1;
            BookingsService.getBooking(uuid);
            expect(bookingsMock.get).toHaveBeenCalledWith({uuid: uuid});
        });

        it("BookingsService:getBookingDetailProduct", function () {
            var productId = 1;
            BookingsService.getBookingDetailProduct(productId);
            expect(productsMock.get).toHaveBeenCalledWith({id: productId});
        });
    });
});