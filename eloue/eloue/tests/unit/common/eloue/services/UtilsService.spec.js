define(["angular-mocks", "eloue/commonApp", "eloue/services", "datejs"], function () {

    describe("Service: UtilsService", function () {

        var UtilsService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {

            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_UtilsService_) {
            UtilsService = _UtilsService_;
        }));

        it("UtilsService should be not null", function () {
            expect(!!UtilsService).toBe(true);
        });

        it("UtilsService:formatDate", function () {
            var date = new Date();
            date.setDate(1);
            date.setMonth(8);
            date.setFullYear(2014);
            var result = UtilsService.formatDate(date, "dd.MM.yyyy");
            expect(result).toEqual("01.09.2014");
        });

        it("UtilsService:formatMessageDate", function () {
            var result = UtilsService.formatMessageDate("08.01.2014", "dd/MM/yyyy", "dd/MM/yyyy hh:mm:ss");
            expect(result).toEqual("01/08/2014 12:00:00");
        });

        it("UtilsService:getIdFromUrl", function () {
            var id = "1208";
            var url = "http://10.0.5.47:8200/api/2.0/users/" + id + "/";
            var result = UtilsService.getIdFromUrl(url);
            expect(result).toEqual(id);
        });

        it("UtilsService:calculatePeriodBetweenDates", function () {
            var startDateString = "01/01/2014 00:00:00", endDateString = "01/02/2014 12:00:00";
            var result = UtilsService.calculatePeriodBetweenDates(startDateString, endDateString);
            expect(result).toEqual({period_days: 1, period_hours: 12});
        });
    });
});
