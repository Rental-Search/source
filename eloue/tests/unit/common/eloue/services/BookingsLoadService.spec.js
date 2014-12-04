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
            spyOn(bookingsMock, "get").and.callThrough();
            spyOn(bookingsMock, "save").and.callThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").and.callThrough();
            spyOn(bookingsParseServiceMock, "parseBookingListItem").and.callThrough();
            spyOn(bookingsParseServiceMock, "parseBooking").and.callThrough();
            spyOn(productsLoadServiceMock, "getProduct").and.callThrough();
        }));

        it("BookingsLoadService should be not null", function () {
            expect(!!BookingsLoadService).toBe(true);
        });
    });
});