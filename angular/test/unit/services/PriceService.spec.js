define(["angular-mocks", "eloue/modules/booking/services/PriceService"], function() {

    describe("Service: PriceService", function () {

        var PriceService, pricesResourceMock;

        beforeEach(module("EloueApp"));
        beforeEach(module("EloueApp.BookingModule"));

        beforeEach(function () {
            pricesResourceMock = {get: function () {
            }};

            module(function($provide) {
                $provide.value("Prices", pricesResourceMock);
            });
        });

        beforeEach(inject(function (_PriceService_) {
            PriceService = _PriceService_;
            spyOn(pricesResourceMock, "get").andCallThrough();
        }));

        it("PriceService should be not null", function() {
            expect(!!PriceService).toBe(true);
        });

        it("PriceService should have a getPricePerDay function", function() {
            expect(angular.isFunction(PriceService.getPricePerDay)).toBe(true);
        });

        it("PriceService should make a call to Prices resource", function () {
            var productId = 1;
            PriceService.getPricePerDay(productId);
            expect(pricesResourceMock.get).toHaveBeenCalledWith({product: productId});
        });
    });
});
