define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: BookingsParseService", function () {

        var BookingsParseService,
            utilsServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            utilsServiceMock = {
                formatDate: function (date, format) {

                },
                calculatePeriodBetweenDates: function(firstDate, secondDate) {
                    return {}
                }
            };
            module(function ($provide) {
                $provide.value("UtilsService", utilsServiceMock);
            });
        });

        beforeEach(inject(function (_BookingsParseService_) {
            BookingsParseService = _BookingsParseService_;
            spyOn(utilsServiceMock, "formatDate").and.callThrough();
            spyOn(utilsServiceMock, "calculatePeriodBetweenDates").and.callThrough();
        }));

        it("BookingsParseService should be not null", function () {
            expect(!!BookingsParseService).toBe(true);
        });

        it("BookingsParseService:parseBookingListItem", function () {
            var bookingData = {}, productData = {}, picturesDataArray = [{image: {thumbnail: "111.png"}}];
            var result = BookingsParseService.parseBookingListItem(bookingData, productData, picturesDataArray);
            expect(result.picture).toEqual(picturesDataArray[0].image.thumbnail);
        });
        it("BookingsParseService:parseBooking", function () {
            var bookingData = {id: 1};
            var result = BookingsParseService.parseBooking(bookingData);
            expect(result.id).toEqual(bookingData.id);
        });
    });
});