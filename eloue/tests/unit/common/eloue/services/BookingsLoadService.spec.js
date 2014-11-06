define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: BookingsLoadService", function () {

        var BookingsLoadService,
            bookingsMock,
            utilsServiceMock,
            bookingsParseServiceMock,
            productsLoadServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            bookingsMock = {
                get: function () {
                },
                save: function () {
                }
            };
            utilsServiceMock = {
                getIdFromUrl: function (url) {

                }
            };
            bookingsParseServiceMock = {
                parseBookingListItem: function (bookingData, productData, picturesDataArray) {

                },
                parseBooking: function (bookingDate) {

                }
            };
            productsLoadServiceMock = {
                getProduct: function (productId) {

                }
            };

            module(function ($provide) {
                $provide.value("Bookings", bookingsMock);
                $provide.value("UtilsService", utilsServiceMock);
                $provide.value("BookingsParseService", bookingsParseServiceMock);
                $provide.value("ProductsLoadService", productsLoadServiceMock);
            });
        });

        beforeEach(inject(function (_BookingsLoadService_) {
            BookingsLoadService = _BookingsLoadService_;
            spyOn(bookingsMock, "get").andCallThrough();
            spyOn(bookingsMock, "save").andCallThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").andCallThrough();
            spyOn(bookingsParseServiceMock, "parseBookingListItem").andCallThrough();
            spyOn(bookingsParseServiceMock, "parseBooking").andCallThrough();
            spyOn(productsLoadServiceMock, "getProduct").andCallThrough();
        }));

        it("BookingsLoadService should be not null", function () {
            expect(!!BookingsLoadService).toBe(true);
        });
    });
});