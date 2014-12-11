define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: UnavailabilityPeriodsService", function () {

        var UnavailabilityPeriodsService,
            unavailabilityPeriodsMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            unavailabilityPeriodsMock = {
                get: function (params) {

                },
                save: function (obj) {

                },
                update: function (id, obj) {

                },
                delete: function (id) {

                }
            };

            module(function ($provide) {
                $provide.value("UnavailabilityPeriods", unavailabilityPeriodsMock);
            });
        });

        beforeEach(inject(function (_UnavailabilityPeriodsService_) {
            UnavailabilityPeriodsService = _UnavailabilityPeriodsService_;
            spyOn(unavailabilityPeriodsMock, "get").andCallThrough();
            spyOn(unavailabilityPeriodsMock, "save").andCallThrough();
            spyOn(unavailabilityPeriodsMock, "update").andCallThrough();
            spyOn(unavailabilityPeriodsMock, "delete").andCallThrough();
        }));

        it("UnavailabilityPeriodsService should be not null", function () {
            expect(!!UnavailabilityPeriodsService).toBe(true);
        });

        it("UnavailabilityPeriodsService:savePeriod", function () {
            var period = {
                id: 1
            };
            UnavailabilityPeriodsService.savePeriod(period);
            expect(unavailabilityPeriodsMock.save).toHaveBeenCalledWith(period);
        });

        it("UnavailabilityPeriodsService:updatePeriod", function () {
            var period = {
                id: 1
            };
            UnavailabilityPeriodsService.updatePeriod(period);
            expect(unavailabilityPeriodsMock.update).toHaveBeenCalledWith({id: period.id}, period);
        });

        it("UnavailabilityPeriodsService:deletePeriod", function () {
            var periodId = 1;
            UnavailabilityPeriodsService.deletePeriod(periodId);
            expect(unavailabilityPeriodsMock.delete).toHaveBeenCalledWith({id: periodId});
        });

        it("UnavailabilityPeriodsService:getByProduct", function () {
            var productId = 1;
            UnavailabilityPeriodsService.getByProduct(productId);
            expect(unavailabilityPeriodsMock.get).toHaveBeenCalledWith({_cache: jasmine.any(Number), product: productId});
        });
    });
});