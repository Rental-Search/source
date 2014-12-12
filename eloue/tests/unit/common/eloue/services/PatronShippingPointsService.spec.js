define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: PatronShippingPointsService", function () {

        var PatronShippingPointsService,
            patronShippingPointsMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            patronShippingPointsMock = {
                get: function () {
                    return {$promise: {}}
                },
                save: function () {
                    return {$promise: {}}
                },
                delete: function () {
                    return {$promise: {}}
                }
            };
            module(function ($provide) {
                $provide.value("PatronShippingPoints", patronShippingPointsMock);
            });
        });

        beforeEach(inject(function (_PatronShippingPointsService_) {
            PatronShippingPointsService = _PatronShippingPointsService_;
            spyOn(patronShippingPointsMock, "get").and.callThrough();
            spyOn(patronShippingPointsMock, "save").and.callThrough();
            spyOn(patronShippingPointsMock, "delete").and.callThrough();
        }));

        it("PatronShippingPointsService should be not null", function () {
            expect(!!PatronShippingPointsService).toBe(true);
        });

        it("PatronShippingPointsService:getByPatronAndBooking", function () {
            var userId = 1, bookingId = 1;
            PatronShippingPointsService.getByPatronAndBooking(userId, bookingId);
            expect(patronShippingPointsMock.get).toHaveBeenCalledWith({_cache: jasmine.any(Number), patron: userId, booking: bookingId});
        });

        it("PatronShippingPointsService:saveShippingPoint", function () {
            var shippingPoint = {};
            PatronShippingPointsService.saveShippingPoint(shippingPoint);
            expect(patronShippingPointsMock.save).toHaveBeenCalledWith(shippingPoint);
        });
    });
});