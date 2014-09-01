define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

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
            var result = UtilsService.formatDate(new Date("09.01.2014"), "dd/MM/yyyy");
            expect(result).toEqual("01/09/2014");
        });

        it("UtilsService:formatMessageDate", function () {
            var result = UtilsService.formatMessageDate("09.01.2014", "dd/MM/yyyy", "dd/MM/yyyy hh:mm:ss");
            expect(result).toEqual("09.01.2014");
        });

//        it("UtilsService:getIdFromUrl", function () {
//            var result = UtilsService.getIdFromUrl();
//            console.log(result);
//        });
//
//        it("UtilsService:calculatePeriodBetweenDates", function () {
//            var result = UtilsService.calculatePeriodBetweenDates();
//            console.log(result);
//        });
    });
});
