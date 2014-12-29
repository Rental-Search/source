define(["angular-mocks", "eloue/controllers/items/ItemsProfitsCtrl"], function() {

    describe("Controller: ItemsProfitsCtrl", function () {

        var ItemsProfitsCtrl,
            scope,
            stateParams,
            bookingsServiceMock,
            simpleServiceResponse = {
                then: function () {
                    return {result: {}};
                }
            };

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            bookingsServiceMock = {
                getBookingsByProduct: function (productId) {
                    console.log("bookingsServiceMock:getBookingsByProduct called with productId = " + productId);
                    return simpleServiceResponse;
                }
            };

            module(function($provide) {
                $provide.value("BookingsService", bookingsServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            stateParams = {
                id: 1
            };

            spyOn(bookingsServiceMock, "getBookingsByProduct").and.callThrough();

            ItemsProfitsCtrl = $controller('ItemsProfitsCtrl', { $scope: scope, $stateParams: stateParams, BookingsService: bookingsServiceMock });
            expect(bookingsServiceMock.getBookingsByProduct).toHaveBeenCalledWith(stateParams.id);
        }));

        it("ItemsProfitsCtrl should be not null", function () {
            expect(!!ItemsProfitsCtrl).toBe(true);
        });

        it("ItemsProfitsCtrl:applyBookings", function () {
            scope.applyBookings();
        });
    });
});