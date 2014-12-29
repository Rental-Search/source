define(["angular-mocks", "eloue/services/UnavailabilityPeriodsService"], function () {

    describe("Service: UnavailabilityPeriodsService", function () {

        var UnavailabilityPeriodsService,
            unavailabilityPeriodsMock,
            simpleResourceResponse = {
                $promise: {
                    then: function () {
                        return {results: []};
                    }
                }
            };

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            unavailabilityPeriodsMock = {
                get: function (params) {
                    return {$promise: {}}
                },
                save: function (obj) {
                    return {$promise: {}}
                },
                update: function (id, obj) {
                    return {$promise: {}}
                },
                delete: function (id) {
                    return {$promise: {}}
                }
            };

            module(function ($provide) {
                $provide.value("UnavailabilityPeriods", unavailabilityPeriodsMock);
            });
        });

        beforeEach(inject(function (_UnavailabilityPeriodsService_) {
            UnavailabilityPeriodsService = _UnavailabilityPeriodsService_;
            spyOn(unavailabilityPeriodsMock, "get").and.callThrough();
            spyOn(unavailabilityPeriodsMock, "save").and.callThrough();
            spyOn(unavailabilityPeriodsMock, "update").and.callThrough();
            spyOn(unavailabilityPeriodsMock, "delete").and.callThrough();
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
            var period = {id: 1};
            UnavailabilityPeriodsService.deletePeriod(period);
            expect(unavailabilityPeriodsMock.delete).toHaveBeenCalledWith({id: period.id});
        });

        it("UnavailabilityPeriodsService:getByProduct", function () {
            var productId = 1;
            UnavailabilityPeriodsService.getByProduct(productId);
            expect(unavailabilityPeriodsMock.get).toHaveBeenCalledWith({_cache: jasmine.any(Number), product: productId});
        });
    });
});