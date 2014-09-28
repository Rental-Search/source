define(["angular-mocks", "datejs", "eloue/controllers/items/ItemsCalendarCtrl"], function () {

    describe("Controller: ItemsCalendarCtrl", function () {

        var ItemsCalendarCtrl,
            scope,
            stateParams,
            bookingsServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            bookingsServiceMock = {
                getBookingsByProduct: function (productId) {
                    console.log("bookingsServiceMock:getBookingsByProduct called with productId = " + productId);
                    return {then: function () {
                        return {response: {}}
                    }}
                }
            };

            module(function ($provide) {
                $provide.value("BookingsService", bookingsServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            stateParams = {
                id: 1
            };

            spyOn(bookingsServiceMock, "getBookingsByProduct").andCallThrough();

            ItemsCalendarCtrl = $controller('ItemsCalendarCtrl', { $scope: scope, $stateParams: stateParams, BookingsService: bookingsServiceMock });
            expect(bookingsServiceMock.getBookingsByProduct).toHaveBeenCalled();
        }));

        it("ItemsCalendarCtrl should be not null", function () {
            expect(!!ItemsCalendarCtrl).toBe(true);
        });

        it("ItemsCalendarCtrl:updateCalendar", function () {
            scope.selectedMonthAndYear = Date.today().getMonth() + " " + Date.today().getFullYear();
            scope.updateCalendar();
        });
    });
});