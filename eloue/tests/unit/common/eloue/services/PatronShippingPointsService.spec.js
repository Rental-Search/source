define(["angular-mocks", "eloue/services/PatronShippingPointsService"], function () {

    describe("Service: PatronShippingPointsService", function () {

        var PatronShippingPointsService,
            patronShippingPointsMock,
            simpleResourceResponse = {
                $promise: {
                    then: function () {
                        return {results: []};
                    }
                }
            };

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            patronShippingPointsMock = {
                get: function () {
                    return simpleResourceResponse;
                },
                save: function () {
                    return simpleResourceResponse;
                },
                delete: function () {
                    return simpleResourceResponse;
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

        it("PatronShippingPointsService:getById", function () {
            var id = 1;
            PatronShippingPointsService.getById(id);
            expect(patronShippingPointsMock.get).toHaveBeenCalledWith({id: id, _cache: jasmine.any(Number)});
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