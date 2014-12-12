define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: BookingsService", function () {

        var BookingsService,
            q,
            bookingsMock,
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

            utilsServiceMock = {
                formatDate: function (date, format) {

                }
            };

            module(function ($provide) {
                $provide.value("Bookings", bookingsMock);
                $provide.value("UtilsService", utilsServiceMock);
            });
        });

        beforeEach(inject(function (_BookingsService_, $q) {
            BookingsService = _BookingsService_;
            q = $q;
            spyOn(bookingsMock, "get").and.callThrough();
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